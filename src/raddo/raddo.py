#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 raddo

 Tries to download all recent RADOLAN ascii files / archives from DWD FTP
 to current directory if files do not exist.

"""

import os
import sys
import re
import glob
import datetime
import argparse
import gdal
import pandas as pd
import xarray as xr

from dateutil.parser import parse
from urllib.request import urlretrieve
from urllib.error import HTTPError
from urllib.error import URLError

from raddo import sort_tars
from raddo import untar
from raddo import __version__

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


RAD_DIR_DWD = ("https://opendata.dwd.de/climate_environment/CDC/"
               "grids_germany/hourly/radolan/recent/asc/")
RAD_DIR_DWD_HIST = ("https://opendata.dwd.de/climate_environment/CDC/"
                    "grids_germany/hourly/radolan/historical/asc/")
RAD_DIR = os.getcwd()

# TODO ($USERCONFIG/.raddo/local_files) ??
FILELIST = ".raddo_local_files.txt"
START_DATE = f"{datetime.datetime.today().year}-01-01"
END_DATE = datetime.datetime.today() - datetime.timedelta(1)  # Yesterday
END_DATE_STR = datetime.datetime.strftime(END_DATE, "%Y-%m-%d")
ERRORS_ALLOWED = 5
VALID_Y = ["y", "Y"]
VALID_N = ["n", "N", ""]

DWD_PROJ = ("+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 "
            "+a=6370040 +b=6370040 +units=m")


class pcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                 rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                 rad_dir=RAD_DIR,
                 errors_allowed=ERRORS_ALLOWED,
                 start_date=START_DATE,
                 end_date=END_DATE,
                 force=False,
                 force_down=False):
    """
    radolan_down()  tries to download all recent RADOLAN ascii files/archives
    from DWD FTP to specified directory if files do not exist.
    A list of dates possibly available (default set to 2019-01-01 until today)
    is used to compare hypothetical available data sets with actual local
    available ones. So file listing on the FTP side is skipped due to
    unreliable connection. Timeout is 60 secs per retrieval attempt and
    50 tries are made.

    PARAMETERS:
    -------------------------
        rad_dir_dwd: string
            Link to Radolan products on DWD FTP server.
            defaults to "https://opendata.dwd.de/climate_environment/CDC/
                         grids_germany/hourly/radolan/recent/asc/")

        rad_dir: string
            local directory to be processed / already containing radolan data.
            defaults to current working directory

        start_date: string
            parsable date string (default "2019-01")

        end_date: string
            parsable date string (defaults to yesterday)

        errors_allowed: integer
            number of tries to download one file (default: 5)
        force:
            Forces local file search. Omits faster check of
            .raddo_local_files.txt".
        force_down:
            Forces download of all files.

    """
    # Set dates
    if end_date == "today":
        end_datetime = datetime.datetime.today()
    elif type(end_date) == datetime.datetime:
        end_datetime = end_date
    else:
        end_datetime = parse(end_date)

    start_datetime = parse(start_date)

    print(pcol.BOLD+pcol.OKBLUE)
    print("-" * 80)
    print(f"[LOCAL]  Radolan directory is set to:\n{rad_dir}\n")
    print(f"[REMOTE] Radolan directory is set to:\n{rad_dir_dwd}\n")
    print(f"searching for data from {start_datetime.date()} - "
          f"{end_datetime.date()}.\n")
    print("-" * 80)
    print(pcol.ENDC)

    fileSet = []
    fileSet_hist = []
    dates_exist = []
    dates_exist_hist = []
    files_success = []
    os.chdir(rad_dir)

    # TODO sensible??
    search = False
    if not local_file_list_exists():
        search = True
        if rad_dir == os.getcwd():
            search = False
    elif force is True:
        search = True
    else:
        dates_exist = [int(f[3:11]) if f[-2:] == "gz" else int(f[3:9])
                       for f in list_of_available_files()]

    # Get filenames if directory is specified
    if search:
        print(str(datetime.datetime.now())[:-4],
              "   getting names of local files in directory:")

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
        create_file_list_savely(fileSet)
        if len(fileSet_hist) > 0:
            update_list_of_available_files(fileSet_hist)

    print()
    print(str(datetime.datetime.now())[:-4],
          f"   {len(dates_exist)} local archive(s) found.\n")

    # avoid searching for todays data:
    delta = 1
    if end_datetime.date() == datetime.datetime.today().date():
        delta -= 1

    # create list of possibly available DATA
    date_list = [start_datetime + datetime.timedelta(days=x)
                 for x in range(
                         int((end_datetime - start_datetime).days) + delta)]
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
        fileSet = list_of_available_files()

        if not len(fileSet) == 0:
            print(str(datetime.datetime.now())[:-4], "   ", end="")
            print(pcol.OKGREEN, end="")
            print(f"Read file list of available files ({FILELIST}).", end="")
            print(pcol.ENDC)

        for f in list_DWD:
            if not ((f in fileSet) or (hist_filename(f) in fileSet)):
                missing_files.append(f)

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

    # try to download all missing files
    for f in missing_files:
        error_count = 0
        while error_count < errors_allowed + 1:

            try:
                print(str(datetime.datetime.now())[:-4],
                      "    [{}] trying {}{}"
                      .format(error_count, rad_dir_dwd, f))
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

            except URLError as e:
                sys.stderr.write(f"\nERROR: {e}\n")
                sys.stderr.write("Do you have internet connection?\n")
                sys.exit(1)

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
                              .format(f, rad_dir_dwd_hist+hist_y+"/"+hist_f),
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
                        else:
                            print(str(datetime.datetime.now())[:-4],
                                  pcol.OKGREEN,
                                  f"   [SUCCESS] {hist_f} has already "
                                  f"been downloaded.\n",
                                  pcol.ENDC)
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

    update_list_of_available_files(files_success)

    return files_success


def local_file_list_exists():
    return os.path.exists(FILELIST)


def create_file_list_savely(available_files):
    if not local_file_list_exists():
        with open(FILELIST, 'a') as fl:
            for f in sorted(available_files):
                fl.write(f+"\n")
        print(str(datetime.datetime.now())[:-4], "   ", end="")
        print(pcol.OKGREEN, end="")
        print(f"Created file list of available files ({FILELIST}).", end="")
        print(pcol.ENDC)


def update_list_of_available_files(new_files):
    if len(new_files) > 0:
        if local_file_list_exists():
            with open(FILELIST, "a") as fl:
                for nf in sorted(new_files):
                    fl.write(nf+"\n")

            print(str(datetime.datetime.now())[:-4], "   ", end="")
            print(pcol.OKGREEN, end="")
            print(f"Updated file list of available files ({FILELIST}) with:",
                  end="")
            print(pcol.ENDC)
            print(new_files)
        else:
            create_file_list_savely(new_files)


def list_of_available_files():
    if local_file_list_exists():
        with open(FILELIST, 'r') as fl:
            filelist = fl.read().splitlines()
        return filelist
    return []


def try_create_directory(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
    except OSError:
        raise
    return directory


def get_asc_files(directories):
    dirs = list(set(list(directories)))
    fl = []
    for d in dirs:
        [fl.append(f) for f in glob.glob(os.path.join(d, "**/*asc"),
                                         recursive=True)]
    return fl


def create_netcdf(filelist, outdir):
    assert type(filelist) == list
    sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                     '   creating NetCDF file...\n')

    outf = os.path.join(outdir, "RADOLAN.nc")

    def time_index_from_filenames(filenames):
        '''helper function to create a pandas DatetimeIndex
        Filename example: 20150520_0164.tif'''
        return pd.DatetimeIndex([pd.Timestamp(f[3:16]) for f in filenames])

    base_f_list = sorted([os.path.basename(f) for f in filelist])
    time = xr.Variable('time', time_index_from_filenames(base_f_list))
    da = xr.concat([xr.open_rasterio(f) for f in filelist], dim=time)
    da = da.to_dataset(name="radolan")
    da = da.rename_dims({'x': 'lon',
                         'y': 'lat'})
    da = da.rename_vars({'x': 'lon',
                         'y': 'lat'})
    da = da.assign_coords({"lon": da.lon,
                           "lat": da.lat})

    # mask nodata (-1) as np.nan && compensate for 1/10 mm
    # (although writing as integer for compressing reasons)
    da['radolan'] = da.radolan.where(da.radolan >= 0) / 10
    da['radolan'].attrs['long_name'] = \
        'Precipitation data from RADOLAN RW Weather Radar Data (DWD)'
    da['radolan'].attrs['units'] = 'mm/h'
    da.to_netcdf(outf, encoding={'radolan': {'dtype': 'int16',
                                             'scale_factor': 0.1,
                                             'zlib': True,
                                             '_FillValue': -9999}})

    sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                     '   done.\n')
    sys.stdout.flush()
    return outf


def create_geotiffs(filelist, outdir):
    assert type(filelist) == list
    sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                     '   creating geotiffs..\n')

    res = []
    for i, f in enumerate(filelist):
        sys.stdout.write('\r' + str(datetime.datetime.now())[:-4] +
                         f'   [{i}]  {os.path.basename(f)}')
        outf = os.path.join(outdir,
                            os.path.splitext(os.path.basename(f))[0] + ".tiff")

        gdal.Warp(outf, f,
                  dstSRS="EPSG:4326",
                  srcSRS=DWD_PROJ,
                  resampleAlg='near',
                  format='GTiff')
        res.append(outf)
    sys.stdout.write('\n' + str(datetime.datetime.now())[:-4] +
                     '   done.\n')
    sys.stdout.flush()
    return res


def user_check():
    do = input("[y/N] ")
    if do in VALID_Y:
        pass
    elif do in VALID_N:
        sys.stderr.write(f"User Interruption.\n")
        sys.exit()


def main():

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        description=(
            ' raddo - utility to download RADOLAN data from DWD servers\n'
            '         and prepare for simple usage.'),
        prog="raddo",
        # usage='run "%(prog)s -h"  for all cli options.'
        )

    parser.add_argument('-u', '--radolan_server_url',
                        required=False,
                        default=RAD_DIR_DWD,
                        action='store', dest='url',
                        help=(f'Path to recent .asc RADOLAN data on '
                              f'DWD servers.\nDefault: {RAD_DIR_DWD}'))

    parser.add_argument('-d', '--directory',
                        required=False,
                        default=f"{os.getcwd()}",
                        action='store', dest='directory',
                        help=(f'Path to local directory where RADOLAN should'
                              f'be (and may already be) saved. Checks for '
                              f'existing files only if this flag is set.'
                              f'\nDefault: {os.getcwd()} (current directory)'))
    parser.add_argument('-s', '--start',
                        required=False,
                        default=START_DATE,
                        action='store', dest='start',
                        help=(f'Start date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {START_DATE} '
                              f'(current year\'s Jan 1st)'))
    parser.add_argument('-e', '--end',
                        required=False,
                        default=END_DATE,
                        action='store', dest='end',
                        help=(f'End date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {END_DATE_STR} (yesterday)'))
    parser.add_argument('-r', '--errors-allowed',
                        required=False,
                        default=ERRORS_ALLOWED,
                        action='store', dest='errors',
                        help=(f'Errors allowed when contacting DWD Server.'
                              f'\nDefault: {ERRORS_ALLOWED}'))
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

    parser.add_argument('-C', '--complete',
                        required=False,
                        default=False,
                        action='store_true', dest='complete',
                        help=(f'Run all subcommands. Same as using flags '
                              f'-fxgn.'))

    parser.add_argument('-y', '--yes',
                        required=False,
                        default=False,
                        action='store_true', dest='yes',
                        help=(f'Skip user input. Just accept to download to '
                              'current directory if not specified otherwise.'))
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

    parser.add_argument('-v', '--version',
                        required=False,
                        default=False,
                        action='store_true', dest='version',
                        help=(f'Print information on software version.'))

    args = parser.parse_args()
    if args.complete:
        args.netcdf = True
        args.geotiff = True
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
        if not args.yes:
            print(f"Do you really want to store RADOLAN data in "
                  f"\"{os.getcwd()}\"?")
            user_check()
    if args.start == START_DATE:
        if not args.yes:
            print(f"Do you really want to download RADOLAN data from "
                  f"{START_DATE} on?")
            user_check()

    assert args.errors < 21, \
        "Error value too high. Please be respectful with the data provider."

    successfull_down = radolan_down(rad_dir_dwd=args.url,
                                    rad_dir=args.directory,
                                    errors_allowed=int(args.errors),
                                    start_date=args.start,
                                    end_date=args.end,
                                    force=args.force,
                                    force_down=args.force_down)
    if len(successfull_down) > 0:
        if args.sort:
            # sort_tars.sort_tars(path=args.directory)
            new_paths = sort_tars.sort_tars(files=successfull_down)
        # TODO only untar successfull_down files
        if args.extract:
            untarred_dirs = untar.untar(files=new_paths)

        if (args.geotiff or args.netcdf) and len(untarred_dirs) > 0:
            tiff_dir = try_create_directory(os.path.join(args.directory,
                                                         "tiff"))
            asc_files = get_asc_files(untarred_dirs)
            gtiff_files = create_geotiffs(asc_files, tiff_dir)
            if args.netcdf:
                create_netcdf(gtiff_files, args.directory)
        else:
            print("Cannot create GeoTiffs - no newly extracted *.asc files.")


if __name__ == "__main__":
    main()
