#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 raddo

 Tries to download all recent RADOLAN ascii files / archives from DWD FTP
 to current directory if files do not exist.

"""

import ast
import os
import sys
import re
import glob
import datetime
import argparse
import tempfile
from osgeo import gdal
import numpy as np
import geopandas as gpd
import xarray as xr
import netCDF4

from dateutil.parser import parse
from urllib.request import urlretrieve
from urllib.error import HTTPError

from raddo import sort_tars
from raddo import untar
from raddo import __version__

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


VALID_Y = ["y", "Y"]
VALID_N = ["n", "N", ""]


class pcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Raddo(object):

    def __init__(self):
        self.FILELIST = ".raddo_local_files.txt"
        self.ERRORS_ALLOWED = 5
        self.RAD_DIR_DWD = ("https://opendata.dwd.de/climate_environment/CDC/"
                            "grids_germany/hourly/radolan/recent/asc/")
        self.RAD_DIR_DWD_HIST = ("https://opendata.dwd.de/climate_environment/CDC/"
                                 "grids_germany/hourly/radolan/historical/asc/")

        self.RAD_DIR = os.getcwd()

        # TODO ($USERCONFIG/.raddo/local_files) ??
        today = datetime.datetime.today()
        self.START_DATE = \
            f"{(today - datetime.timedelta(days=14)).date()}"
        self.END_DATE = datetime.datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0) \
            - datetime.timedelta(days=1)
        self.END_DATE_STR = datetime.datetime.strftime(self.END_DATE,
                                                       "%Y-%m-%d")

        self.DWD_PROJ = ("+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 "
                         "+a=6370040 +b=6370040 +units=m")
        self.geotiff_mask = None
        self.buffer = 1400

    def radolan_down(self, *args, **kwargs):
        """
        radolan_down()  tries to download all recent RADOLAN ascii files/
        archives from DWD FTP to specified directory if files do not exist.
        A list of dates possibly available (default set to 2019-01-01 until today)
        is used to compare hypothetical available data sets with actual local
        available ones. So file listing on the FTP side is skipped due to
        unreliable connection. Timeout is 60 secs per retrieval attempt and
        50 tries are made.

        Keyword Arguments:
        -------------------------
            rad_dir_dwd: string
                Link to Radolan products on DWD FTP server.
                defaults to "https://opendata.dwd.de/climate_environment/CDC/\
                            grids_germany/hourly/radolan/recent/asc/")

            rad_dir_dwd_hist: string
                Link to Radolan products on DWD FTP server.
                defaults to "https://opendata.dwd.de/climate_environment/CDC/"\
                             grids_germany/hourly/radolan/historical/asc/"

            rad_dir: string
                local directory to be processed / already containing radolan data.
                defaults to current working directory

            start_date: string
                parsable date string (default: 14 days ago)

            end_date: string
                parsable date string (default: yesterday)

            no_time_correction: bool
                omit RADOLAN time correction to full hourly values

            errors_allowed: integer
                number of tries to download one file (default: 5)
            force:
                Forces local file search. Omits faster check of
                .raddo_local_files.txt".
            force_down:
                Forces download of all files.
            mask:
                Mask shapefile.
            buffer:
                Buffer in meter around shapefile mask.
            coords: string of tuple
                Coordinates ("(lat,lon)") to extract precipitation for.
                Exclusive with mask.

        """

        rad_dir_dwd = kwargs.get('rad_dir_dwd', self.RAD_DIR_DWD)
        rad_dir_dwd_hist = kwargs.get('rad_dir_dwd_hist', self.RAD_DIR_DWD_HIST)
        rad_dir = kwargs.get('rad_dir', self.RAD_DIR)
        errors_allowed = kwargs.get('errors_allowed', self.ERRORS_ALLOWED)
        start_date = kwargs.get('start_date', self.START_DATE)
        end_date = kwargs.get('end_date', self.END_DATE)
        self.no_time_correction = kwargs.get('no_time_correction', False)
        force = kwargs.get('force', False)
        force_down = kwargs.get('force_down', False)
        self.yes = kwargs.get('yes', False)
        mask = kwargs.get('mask', None)
        self.buffer = kwargs.get('buffer', self.buffer)
        if mask is not None:
            self.read_mask(mask)
        coords = kwargs.get('coords', None)
        if coords is not None:
            self.read_coords(coords)

        # Set dates
        if end_date == "today":
            self.end_datetime = datetime.datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif type(end_date) == datetime.datetime:
            self.end_datetime = end_date
        else:
            try:
                self.end_datetime = parse(end_date)
            except ValueError as e:
                print(e)
                sys.exit(1)

        # Set max end date to yesterday:
        if self.end_datetime.date() == datetime.datetime.today().date():
            self.end_datetime = \
                datetime.datetime.today().replace(
                    hour=0, minute=0, second=0, microsecond=0) \
                - datetime.timedelta(days=1)

        try:
            self.start_datetime = parse(start_date)
            assert (self.end_datetime - self.start_datetime).days > -1, \
                "End date is before start date."
        except ValueError as e:
            sys.stderr.write(
                f"[ERROR]: Start date could not be parsed: {start_date}\n")
            sys.stderr.write(f"{e}\n\n")
            sys.exit(1)
        except AssertionError as e:
            sys.stderr.write(
                f"[ERROR]: {e}\n\n")
            sys.exit(1)

        self.timestamps = \
            np.arange(self.start_datetime,
                      self.end_datetime+datetime.timedelta(days=1),
                      datetime.timedelta(hours=1)
                      ).astype(datetime.datetime).tolist()

        print(pcol.BOLD+pcol.OKBLUE)
        print("-" * 80)
        print(f"[LOCAL]  Radolan directory is set to:\n{rad_dir}\n")
        print(f"[REMOTE] Radolan directory is set to:\n{rad_dir_dwd}\n")
        print(f"searching for data from {self.start_datetime.date()} - "
              f"{self.end_datetime.date()}.\n")
        print("-" * 80)
        print(pcol.ENDC)

        fileSet = []
        fileSet_hist = []
        dates_exist = []
        dates_exist_hist = []
        files_success = []

        if not os.path.isdir(rad_dir):
            if not self.yes:
                if user_check(f"The specified RADOLAN directory\n  ==> "
                              f"'{os.path.abspath(rad_dir)}'\ndoes not "
                              f"exist. Should it be created?"):
                    os.makedirs(os.path.abspath(rad_dir))
                else:
                    sys.stdout.write("\nExiting.\n\n")
                    sys.exit(0)
            else:
                os.makedirs(rad_dir)
        os.chdir(rad_dir)

        search = not self.local_file_list_exists()
        if force or search:
            search = True
        else:
            dates_exist = [int(f[3:11]) if f[-2:] == "gz" else int(f[3:9])
                           for f in self.list_of_available_files]

        # Get filenames if directory is specified
        if search:
            print(str(datetime.datetime.now())[:-4],
                  "   Getting names of local files in directory:")

            for dir_, _, files in os.walk(rad_dir):
                print(f"                          ...{dir_[-30:]}          \r",
                      end="")
                for fileName in files:
                    pattern = r"RW-\d{8}\.tar\.gz$"
                    pattern_hist = r"RW-\d{6}\.tar$"
                    if re.match(pattern, fileName) is not None:
                        fileSet.append(fileName)
                        dates_exist.append(int(fileName[3:11]))
                    if re.match(pattern_hist, fileName) is not None:
                        fileSet_hist.append(fileName)
                        dates_exist_hist.append(int(fileName[3:9]))
            self.create_file_list_savely(fileSet)
            if len(fileSet_hist) > 0:
                self.update_list_of_available_files(fileSet_hist)

        print()
        print(str(datetime.datetime.now())[:-4],
              f"   {len(dates_exist)} local archive(s) found.\n")

        # avoid searching for todays data:
        delta = 1
        if self.end_datetime.date() == datetime.datetime.today().date():
            delta -= 1

        # create list of possibly available DATA
        date_list = [self.start_datetime + datetime.timedelta(days=x)
                     for x in range(
                            int((self.end_datetime - self.start_datetime).days) + delta)]
        list_DWD = ["RW-{}.tar.gz"
                    .format(datetime.datetime.strftime(x, format="%Y%m%d"))
                    for x in date_list]
        # list_DWD_hist = list(set([
        #     "RW-{}.tar".format(datetime.datetime.strftime(x, format="%Y%m"))
        #     for x in date_list]))

        def hist_filename(filename):
            return filename[:9]+".tar"

        # Compare local and remote list
        missing_files = []
        if force_down:
            missing_files = list_DWD.copy()
        elif search:
            for f in list_DWD:
                if f not in fileSet:
                    if hist_filename(f) not in fileSet_hist:
                        missing_files.append(f)
                else:
                    files_success.append(f)
        else:
            fileSet = self.list_of_available_files

            if not len(fileSet) == 0:
                print(str(datetime.datetime.now())[:-4], "   ", end="")
                print(pcol.OKGREEN, end="")
                print(f"Read file list of available files ({self.FILELIST}).", end="")
                print(pcol.ENDC)

            for f in list_DWD:
                if not ((f in fileSet) or (hist_filename(f) in fileSet)):
                    missing_files.append(f)
                else:
                    files_success.append(f)

        if len(missing_files) > 0:
            print(str(datetime.datetime.now())[:-4], "   {} file(s) missing.\n"
                  .format(len(missing_files)))
            print("Missing files:\n")
            if len(missing_files) > 10:
                for item in missing_files[:5] + ['...'] + missing_files[-5:]:
                    print(item)
            else:
                for item in missing_files:
                    print(item)
            print()
        else:
            print(str(datetime.datetime.now())[:-4], "   No files missing.\n")

        self.hist_files = False
        # try to download all missing files
        for f in missing_files:
            error_count = 0
            while error_count < errors_allowed + 1:

                try:
                    print(str(datetime.datetime.now())[:-4],
                          "    [{}] trying {}{}"
                          .format(error_count, rad_dir_dwd[-22:], f))
                    urlretrieve(rad_dir_dwd+f, f)
                    size = os.path.getsize(f)
                    if size == 0:
                        print('file size of {}==0! Removing'.format(f))
                        os.remove(f)
                        continue
                    print(str(datetime.datetime.now())[:-4],
                          "   [SUCCESS] {} downloaded.\n".format(f))
                    files_success.append(f)
                    break

                # except URLError as e:
                #     sys.stderr.write(f"\nERROR: {e}\n")
                #     sys.stderr.write("Do you have internet connection?\n")
                #     sys.exit(1)

                except HTTPError as err:
                    if err.code == 404:
                        # try historical data
                        hist_f = f[:9]+".tar"
                        hist_y = f[3:7]
                        # hist_m = f[7:9]
                        try:
                            print(str(datetime.datetime.now())[:-4],
                                  pcol.WARNING,
                                  "   [ERROR] {}. "
                                  "Now trying historical data."
                                  .format(f, rad_dir_dwd_hist[-20:]+hist_y+"/"+hist_f),
                                  pcol.ENDC)
                            if hist_f not in os.listdir():
                                urlretrieve(rad_dir_dwd_hist+hist_y+"/"+hist_f,
                                            hist_f)
                                size = os.path.getsize(hist_f)
                                if size == 0:
                                    print(
                                        pcol.WARNING,
                                        f'file size of {hist_f}==0! Removing.',
                                        pcol.WARNING)
                                    os.remove(hist_f)
                                    continue
                                print(str(datetime.datetime.now())[:-4],
                                      pcol.OKGREEN,
                                      f"   [SUCCESS] {hist_f} downloaded.\n",
                                      pcol.ENDC)
                                files_success.append(hist_f)
                                self.hist_files = True
                            else:
                                print(str(datetime.datetime.now())[:-4],
                                      pcol.OKGREEN,
                                      f"   [SUCCESS] {hist_f} has already "
                                      f"been downloaded.\n",
                                      pcol.ENDC)
                                files_success.append(hist_f)
                                self.hist_files = True
                            break

                        except Exception as e:
                            print(str(datetime.datetime.now())[:-4],
                                  pcol.WARNING,
                                  f"   [ERROR] {e}\n",
                                  pcol.ENDC)
                            error_count += 1

                if error_count is errors_allowed+1:
                    print("\n", str(datetime.datetime.now())[:-4],
                          pcol.FAIL,
                          "   [ERROR] Exceeded requests ({}) for {}!"
                          .format(error_count, f),
                          pcol.ENDC)

        self.update_list_of_available_files(files_success)

        return files_success

    def local_file_list_exists(self):
        return os.path.exists(self.FILELIST)

    def create_file_list_savely(self, available_files):
        if not self.local_file_list_exists():
            with open(self.FILELIST, 'a') as fl:
                for f in sorted(available_files):
                    fl.write(f+"\n")
            print(str(datetime.datetime.now())[:-4], "   ", end="")
            print(pcol.OKGREEN, end="")
            print(f"Created file list of available files ({self.FILELIST}).", end="")
            print(pcol.ENDC)

    def update_list_of_available_files(self, new_files):
        new_files = sorted(new_files)
        if len(new_files) > 0:
            if self.local_file_list_exists():
                # TODO add function to prune duplicates..
                with open(self.FILELIST, "a") as fl:
                    for nf in new_files:
                        fl.write(nf+"\n")

                print(str(datetime.datetime.now())[:-4], "   ", end="")
                print(pcol.OKGREEN, end="")
                print(f"Updated file list of available files ({self.FILELIST}) with:",
                      end="")
                print(pcol.ENDC)
                if len(new_files) > 20:
                    print(new_files[:10])
                    print("...")
                    print(new_files[-10:])
                else:
                    print(new_files)
            else:
                self.create_file_list_savely(new_files)

    @property
    def list_of_available_files(self):
        if self.local_file_list_exists():
            with open(self.FILELIST, 'r') as fl:
                filelist = fl.read().splitlines()
            return filelist
        return []

    @classmethod
    def try_create_directory(self, directory):
        try:
            os.makedirs(directory)
        except FileExistsError:
            pass
        except OSError:
            raise
        return directory

    def get_asc_files(self, directories):
        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   Getting available *.asc file names...\n\n')
        dirs = list(set(list(directories)))
        fl = []
        for d in dirs:
            [fl.append(f) for f in sorted(glob.glob(os.path.join(d, "**/*asc"),
                                                    recursive=True))
             if self._get_date(os.path.basename(f),
                               self.no_time_correction)[1]
             in self.timestamps]

        return fl

    def _get_date(self, filename, no_time_correction=False):
        f = os.path.basename(filename)
        year = int(f[3:7])
        mon = int(f[7:9])
        day = int(f[9:11])
        hour = int(f[12:14])
        minu = int(f[14:16])
        if not no_time_correction:
            minu = 0
        return f, datetime.datetime(year, mon, day,
                                    hour, minu, 0)

    def _check_netcdf_outf(self, outf):
        if outf is None:
            outf = (f"RADOLAN_{self.start_datetime.strftime('%Y%m%d')}"
                    f"_{self.end_datetime.strftime('%Y%m%d')}.nc")
        else:
            if not os.path.splitext(outf)[1] == ".nc":
                outf = os.path.splitext(outf)[0] + ".nc"
        return outf

    def create_netcdf(self, filelist, outdir, outf=None,
                      no_time_correction=False):
        assert type(filelist) == list
        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   Creating NetCDF file:\n' + 25*" ")
        filelist = sorted(filelist)

        outf = self._check_netcdf_outf(outf)
        outf = os.path.join(outdir, outf)
        fc = 1
        a_outf = outf
        while True:
            if not os.path.isfile(a_outf):
                break
            else:
                a_outf = outf[:-3] + f"_{fc}" + outf[-3:]
            fc += 1
        outf = a_outf
        del a_outf
        sys.stdout.write(f'{pcol.OKBLUE}{outf}{pcol.ENDC}\n')
        self.netcdf_file_name = outf


        # Initialize netCDF
        ds = gdal.Open(filelist[0])
        a = ds.ReadAsArray()
        b = ds.GetGeoTransform()
        nlat, nlon = np.shape(a)
        lon = np.arange(nlon) * b[1] + b[0]
        lat = np.arange(nlat) * b[5] + b[3]

        nco = netCDF4.Dataset(outf, 'w', clobber=True)

        # create dimensions, variables and attributes:
        nco.createDimension('lon', nlon)
        nco.createDimension('lat', nlat)
        nco.createDimension('time', None)

        lono = nco.createVariable('lon', 'f4', ('lon'))
        lono.units = 'degrees_east'
        lono.standard_name = 'longitude'
        lato = nco.createVariable('lat', 'f4', ('lat'))
        lato.units = 'degrees_north'
        lato.standard_name = 'latitude'

        basedate = datetime.datetime(2000, 1, 1, 0, 0, 0)
        timeo = nco.createVariable('time', 'f4', ('time'))
        timeo.units = 'hours since 2000-01-01 00:00:00'
        timeo.standard_name = 'time'

        # create container variable for CRS: lon/lat WGS84 datum
        crso = nco.createVariable('crs', 'i4')
        crso.long_name = 'Lon/Lat Coords in WGS84'
        crso.grid_mapping_name = 'latitude_longitude'
        crso.longitude_of_prime_meridian = 0.0
        crso.semi_major_axis = 6378137.0
        crso.inverse_flattening = 298.257223563

        # create short integer variable for temperature data, with chunking
        chunk_lon = 16
        chunk_lat = 16
        chunk_time = 24
        prco = nco.createVariable('prc', 'f4',  ('time', 'lat', 'lon'),
                                  zlib=True,
                                  # chunksizes=[
                                      # chunk_time, chunk_lat, chunk_lon],
                                  fill_value=-9999)
        prco.units = 'mm/h'
        # prco.scale_factor = 0.1
        # prco.add_offset = 0.00
        prco.long_name = \
            'precipitation data from RADOLAN RW Weather Radar Data (DWD)'
        prco.standard_name = \
            'precipitation'
        prco.grid_mapping = 'crs'
        prco.set_auto_maskandscale(False)

        nco.Conventions = 'CF-1.6'

        # write lon,lat
        lono[:] = lon
        lato[:] = lat

        itime = 0

        try:
            missingdates = []
            assert len(self.timestamps) == len(filelist), "Missing dates!"
        except AssertionError as e:
            sys.stderr.write(f"\n{e}\n")
            sys.stderr.write(f"length timestamps: {len(self.timestamps)}"
                             + "\n" + f"length filelist: {len(filelist)}\n\n")
            sys.stderr.write(str(self.start_datetime))
            sys.stderr.write(str(self.end_datetime))
            # sys.stderr.write(str(self.timestamps))
            # sys.stderr.write(str(filelist))

            sys.stdout.write('\r' + str(datetime.datetime.now())[:-4] +
                             f'   Getting missing dates..\n')
            file_dates = [self._get_date(f, no_time_correction)[1] for f in filelist]
            missingdates = [t for t in self.timestamps if t not in file_dates]
            [sys.stdout.write(f"{d}\n") for d in missingdates]
            sys.stdout.write("\n")

        i = 0
        for tdate in self.timestamps:
            if tdate in missingdates:
                dtime = (tdate-basedate).total_seconds()/3600.
                timeo[itime] = dtime
                prco[itime, :, :] = a * np.nan
                itime = itime + 1
                continue
                assert False, "This should not happen!"
            else:
                fi, fdate = self._get_date(filelist[i], no_time_correction)

            if no_time_correction:
                # sys.sdterr("Cannot assert time correctnes..")
                pass
            else:
                assert fdate == tdate
            sys.stdout.write('\r' + str(datetime.datetime.now())[:-4] +
                             f'   [{i+1} / {len(self.timestamps)}]  '
                             f'{os.path.basename(filelist[i])}')
            dtime = (fdate-basedate).total_seconds()/3600.
            timeo[itime] = dtime

            prc = gdal.Open(filelist[i])
            a = prc.ReadAsArray() / 10  # get data
            a[a < 0] = -9999
            prco[itime, :, :] = a  # 1/10 mm in RADOLAN data
            itime = itime + 1
            i += 1

        nco.missing_dates = str(missingdates)
        nco.close()

        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   done.\n')
        sys.stdout.flush()
        return outf

    def create_geotiffs(self, filelist, outdir):
        assert type(filelist) == list
        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   Creating geotiffs..\n')

        res = []
        for i, f in enumerate(filelist):
            outf = os.path.join(
                outdir,
                os.path.splitext(os.path.basename(f))[0] + ".tiff")

            if not os.path.isfile(outf):
                sys.stdout.write('\r' + str(datetime.datetime.now())[:-4] +
                                 f'   [{i+1} / {len(filelist)}]  '
                                 f'Creating {os.path.basename(outf)}')
                if self.geotiff_mask is not None:
                    outf_suffix = "_mask"
                    outf = os.path.splitext(outf)[0] + outf_suffix + ".tiff"
                    gdal.Warp(outf, f,
                              dstSRS="EPSG:4326",
                              srcSRS=self.DWD_PROJ,
                              cutlineDSName=self.geotiff_mask,
                              cropToCutline=True,
                              format='GTiff')
                else:
                    gdal.Warp(outf, f,
                              dstSRS="EPSG:4326",
                              srcSRS=self.DWD_PROJ,
                              format='GTiff')
            else:
                sys.stdout.write('\r' + str(datetime.datetime.now())[:-4] +
                                 f'   [{i+1} / {len(filelist)}]  '
                                 f'{os.path.basename(outf)} already exists.')
            res.append(outf)
        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   done.\n')
        sys.stdout.flush()
        return res

    def create_point_from_netcdf(self):
        sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                         '   Creating CSV file:\n' + 25*" ")
        csv_outf = os.path.splitext(self.netcdf_file_name)[0] + \
            f"_{self.lon}__{self.lat}".replace(".", "_") + \
            ".csv"
        ds = xr.open_dataset(self.netcdf_file_name)
        da = ds['prc'].sel(lat=self.lat, lon=self.lon, method="nearest")
        da.name ="precipitation"
        da.to_series().to_csv(csv_outf)
        sys.stdout.write(f'{pcol.OKBLUE}{csv_outf}{pcol.ENDC}\n')


    def read_mask(self, maskfile):
        mf = gpd.read_file(maskfile)
        mf = mf.to_crs({'init': 'epsg:32632'})
        gtypes = list(set(mf.geometry.geom_type))
        assert len(gtypes) == 1, \
            "Multiple geometry types in maskfile ({maskfile})!"

        # create centroids if multi poligons
        # if mf.geom_type == 'Polygon' and len(mf) > 1:
        #     mf = mf.centroids()

        with tempfile.NamedTemporaryFile(suffix=".shp") as tmpf:
            self.geotiff_mask = tmpf.name

            # self.mask_bounds = gpd.GeoDataFrame(
            #     crs=mf.crs,
            #     geometry=mf.unary_union.buffer(self.buffer))

        # unary_union?
        if gtypes == "Polygon":
            mf['diss'] = 1
            mf = mf.dissolve(by="diss")
        if gtypes == "Point" and len(mf) == 1 and self.buffer < 1400:
            if user_check("This buffer might not cath any RADOLAN cells. "
                          "Do you want to increase the size to 1400m?"):
                self.buffer = 1400

        buff = mf.buffer(self.buffer)
        self.mask_bounds = buff.to_crs({'init': 'epsg:4326'})

        mf = mf.to_crs({'init': 'epsg:4326'})
        self.mask_bounds.to_file(self.geotiff_mask)

        self.mask_total_bounds = mf.total_bounds
        self.mask_gdf = mf
        self.mask_type = mf.geom_type

    def read_coords(self, coords):
        try:
            sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                             '   Reading coordinates:\n' + 25*" ")
            coord_eval = ast.literal_eval(coords)
            assert type(coord_eval) == tuple
            self.lon, self.lat = coord_eval
            sys.stdout.write(f"{pcol.OKBLUE}"
                             f"longitude: {self.lon}, latitude: {self.lat}"
                             f"{pcol.ENDC}\n")
        except:
            sys.stderr.write(f"{pcol.WARNING}Point coordinates need to be "
                             f"specified like so: ")
            sys.stderr.write("\"-p 12.2,48.5\"  [lon,lat].\n")
            sys.exit()

def user_check(question):
    sys.stdout.write(question+" ")
    do = input("[y/N] ")
    if do in VALID_Y:
        return True
    elif do in VALID_N:
        return False


def main():

    rd = Raddo()

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        description=(
            ' raddo - utility to download and preprocess RADOLAN RW\n'
            '         weather radar data from DWD servers.'),
        prog="raddo",
        # usage='run "%(prog)s -h"  for all cli options.'
        )

    parser.add_argument('-s', '--start',
                        required=False,
                        default=rd.START_DATE,
                        action='store', dest='start',
                        help=(f'Start date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {rd.START_DATE} '
                              f'(14 days ago).'))
    parser.add_argument('-e', '--end',
                        required=False,
                        default=rd.END_DATE,
                        action='store', dest='end',
                        help=(f'End date as parsable string '
                              f'(e.g. "2020-05-20").'
                              f'\nDefault: {rd.END_DATE_STR} (yesterday)'))

    parser.add_argument('-d', '--directory',
                        required=False,
                        default=f"{os.getcwd()}",
                        action='store', dest='directory',
                        help=(
                            f'Absolute path to local directory where RADOLAN'
                            f' data should be (and may already be) saved. Ch'
                            f'ecks for existing files only if this flag is se'
                            f't.\nDefault: {os.getcwd()} (current directory)'))

    parser.add_argument('-C', '--complete',
                        required=False,
                        default=False,
                        action='store_true', dest='complete',
                        help=(f'Run all subcommands. Same as using flags '
                              f'-fxgn.'))

    parser.add_argument('-f', '--sort-in-folders',
                        required=False,
                        default=False,
                        action='store_true', dest='sort',
                        help=(f'Should the data be sorted in folders?'))

    parser.add_argument('-x', '--extract',
                        required=False,
                        default=False,
                        action='store_true', dest='extract',
                        help=(f'Should the data be extracted?'))

    parser.add_argument('-g', '--geotiff',
                        required=False,
                        default=False,
                        action='store_true', dest='geotiff',
                        help=(f'Set if GeoTiffs in EPSG:4326 should be '
                              f'created for newly downloaded files.'))

    parser.add_argument('-n', '--netcdf',
                        required=False,
                        default=False,
                        action='store_true', dest='netcdf',
                        help=(f'Create a NetCDF from GeoTiffs?'))

    parser.add_argument('-N', '--netcdf-file',
                        required=False,
                        default=None,
                        action='store', dest='outfile',
                        help=(f'Name of the output NetCDF file.'))

    parser.add_argument('-m', '--mask',
                        required=False,
                        default=False,
                        action='store', dest='mask',
                        help=(f'Use mask when creating NetCDF.'))

    parser.add_argument('-p', '--point',
                        required=False,
                        default=False,
                        action='store', dest='point',
                        help=(f'Extract precipitation for specific '
                              f'point coordinates.'))

    parser.add_argument('-b', '--buffer',
                        required=False,
                        default=1400,
                        action='store', dest='buffersize',
                        help=(f'Buffer in meter around mask shapefile'
                              ' (Default 1400m).'))

    # parser.add_argument('-q', '--quiet',
    #                     required=False,
    #                     default=False,
    #                     action='store_true', dest='quiet',
    #                     help=(f'Be quiet.'))

    parser.add_argument('-F', '--force',
                        required=False,
                        default=False,
                        action='store_true', dest='force',
                        help=(f'Forces local file search. Omits faster check '
                              'of ".raddo_local_files.txt".'))

    parser.add_argument('-D', '--force-download',
                        required=False,
                        default=False,
                        action='store_true', dest='force_down',
                        help=(f'Forces download of all files.'))

    parser.add_argument('-y', '--yes',
                        required=False,
                        default=False,
                        action='store_true', dest='yes',
                        help=(f'Skip user input. Just accept to download to '
                              'current directory if not specified otherwise.'))

    parser.add_argument('-v', '--version',
                        required=False,
                        default=False,
                        action='store_true', dest='version',
                        help=(f'Print information on software version.'))

    parser.add_argument('-u', '--radolan_server_url',
                        required=False,
                        default=rd.RAD_DIR_DWD,
                        action='store', dest='url',
                        help=(f'Path to recent .asc RADOLAN data on '
                              f'DWD servers.\nDefault: {rd.RAD_DIR_DWD}'))

    parser.add_argument('-r', '--errors-allowed',
                        required=False,
                        default=rd.ERRORS_ALLOWED,
                        action='store', dest='errors',
                        help=(f'Errors allowed when contacting DWD Server.'
                              f'\nDefault: {rd.ERRORS_ALLOWED}'))

    parser.add_argument('-t', '--no-time-correction',
                        required=False,
                        default=False,
                        action='store_true', dest='tcorr',
                        help=(f'Omit time adjustment to previous hour in '
                              f'netCDF file creation and just use RADOLANs '
                              f'sum up time HH:50 (Default: false).'))


    args = parser.parse_args()
    if args.complete:
        args.netcdf = True
        args.geotiff = True
        args.extract = True
        args.sort = True

    if (args.geotiff or args.netcdf or args.point):
        args.extract = True
        args.sort = True

    # print version
    if args.version:
        sys.stdout.write(f"raddo {__version__}\n")
        sys.exit()

    # if not args.quiet:
    sys.stdout.write(
        pcol.HEADER + 59*'=' + '\n' +
        parser.description + "\n" +
        59*"=" + pcol.ENDC + "\n\n")

    # if no -d flag:
    if args.directory == os.getcwd():
        # if (args.start == rd.START_DATE) & (args.end == rd.END_DATE):
            # sys.stdout.write(f"{parser.print_help()}\n\n")

        if not args.yes:
            if not user_check(f"Do you really want to store RADOLAN data in "
                              f"\"{os.getcwd()}\"?"):
                sys.stderr.write(f"User Interruption.\n")
                sys.exit()
    args.directory = os.path.abspath(args.directory)

    if args.start == rd.START_DATE:
        if not args.yes:
            if not user_check(f"Do you really want to download RADOLAN data from "
                              f"{rd.START_DATE} on?"):
                sys.stderr.write(f"User Interruption.\n")
                sys.exit()
    assert args.errors < 21, \
        "Error value too high. Please be respectful with the data provider."

    successfull_down = rd.radolan_down(rad_dir_dwd=args.url,
                                       rad_dir=args.directory,
                                       errors_allowed=int(args.errors),
                                       start_date=args.start,
                                       end_date=args.end,
                                       no_time_correction=args.tcorr,
                                       force=args.force,
                                       force_down=args.force_down,
                                       yes=args.yes,
                                       buffer=args.buffersize)
    if len(successfull_down) > 0:
        new_paths = []
        untarred_dirs = []
        if args.sort:
            new_paths = sort_tars.sort_tars(files=successfull_down)
        if args.extract:
            untarred_dirs = untar.untar(files=new_paths, hist=rd.hist_files)

        if (args.geotiff or args.netcdf or args.point):
            if len(untarred_dirs) > 0:
                asc_files = rd.get_asc_files(untarred_dirs)

                if args.mask:
                    rd.read_mask(args.mask)
                if args.point:
                    try:
                        assert args.mask is False, \
                            "Only specify mask or point coordinates!"
                    except AssertionError as e:
                        sys.stderr.write(f"{e}")
                        sys.exit()
                    rd.read_coords(args.point)

            # create tiff directory
            if args.geotiff:
                tiff_dir = rd.try_create_directory(
                    os.path.join(os.path.abspath(args.directory), "tiff"))
                if not args.yes:
                    if len(asc_files) > 7 * 24:
                        if not user_check("Do you really want to create "
                                          f"{len(asc_files)} geotiffs?\n[These"
                                          " files are only created if not "
                                          "already available.]"):
                            sys.exit("\nExiting.")
                # create geotiffs
                gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)

            # create temporary directory if geotiffs are not wanted:
            else:
                args.yes = True
                # TODO change to current dir (avoid /tmp overflow?)
                tmpd = tempfile.TemporaryDirectory()
                tiff_dir = tmpd.name
                # create temporary geotiffs
                gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
            # create netcdf file
            if args.netcdf:
                rd.create_netcdf(gtiff_files,
                                 args.directory,
                                 args.outfile,
                                 args.tcorr)
            if args.point:
                if not args.netcdf:
                    if args.outfile is None:
                        netcdf_outf = tempfile.NamedTemporaryFile(
                            prefix="RADOLAN_TEMP_").name
                    else:
                        netcdf_outf = args.outfile
                    rd.create_netcdf(gtiff_files,
                                     args.directory,
                                     netcdf_outf,
                                     args.tcorr)
                rd.create_point_from_netcdf()

        else:
            print("Cannot create GeoTiffs - no newly extracted *.asc files.")

        try:
            tmpd.cleanup()
        except NameError:
            pass


if __name__ == "__main__":
    main()
