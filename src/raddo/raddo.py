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

from dateutil.parser import parse
from urllib.request import urlretrieve
from urllib.error import HTTPError

from raddo import sort_tars
from raddo import untar
from raddo import __version__

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


rad_dir_dwd = ("https://opendata.dwd.de/climate_environment/CDC/"
               "grids_germany/hourly/radolan/recent/asc/")
rad_dir_dwd_hist = ("https://opendata.dwd.de/climate_environment/CDC/"
                    "grids_germany/hourly/radolan/historical/asc/")
rad_dir = os.getcwd()
# TODO ($USERCONFIG/.raddo/local_files) ??
FILELIST = ".raddo_local_files.txt"
start_date = f"{datetime.datetime.today().year}-01-01"
end_date = datetime.datetime.today() - datetime.timedelta(1)  # Yesterday
end_date_str = datetime.datetime.strftime(end_date, "%Y-%m-%d")
errors_allowed = 5
valid_y = ["y", "Y"]
valid_n = ["n", "N", ""]


class pcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def radolan_down(rad_dir_dwd=rad_dir_dwd,
                 rad_dir=rad_dir,
                 errors_allowed=errors_allowed,
                 start_date=start_date,
                 end_date=end_date):
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
    if search:
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
                # response = urlopen("{}{}".format(rad_dir_dwd, f),
                #                            timeout=60)
                # with open(f, "w") as dest:
                #     dest.write(response.read().decode(response.headers.get_content_charset()))
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
        [fl.append(f) for f in glob.glob(os.path.join(d, "*asc"),
                                         recursive=True)]
    return fl


def create_geotiffs(filelist, outdir):
    for f in filelist:

        outf = os.path.join(outdir,
                            os.path.splitext(os.path.basename(f))[0] + ".tiff")
        reproject = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "reproject_radolan_geotiff.sh")
        os.system(f"{reproject} {f} {outf}")


def main():

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        description=('Utility to download RADOLAN data from DWD servers.'),
        prog="raddo",
        # usage='%(prog)s directory [-h] [-p]'
        )

    parser.add_argument('-u', '--radolan_server_url',
                        required=False,
                        default=rad_dir_dwd,
                        action='store', dest='url',
                        help=(f'Path to recent .asc RADOLAN data on '
                              f'DWD servers.\nDefault: {rad_dir_dwd}'))

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
                        default=start_date,
                        action='store', dest='start',
                        help=(f'Start date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {start_date} '
                              f'(current year\'s Jan 1st)'))
    parser.add_argument('-e', '--end',
                        required=False,
                        default=end_date,
                        action='store', dest='end',
                        help=(f'End date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {end_date_str} (yesterday)'))
    parser.add_argument('-r', '--errors-allowed',
                        required=False,
                        default=errors_allowed,
                        action='store', dest='errors',
                        help=(f'Errors allowed when contacting DWD Server.'
                              f'\nDefault: {errors_allowed}'))
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
    parser.add_argument('-y', '--yes',
                        required=False,
                        default=False,
                        action='store_true', dest='yes',
                        help=(f'Skip user input. Just accept to download to '
                              'current directory if not specified otherwise.'))
    parser.add_argument('-g', '--geotiff',
                        required=False,
                        default=False,
                        action='store_true', dest='geotiff',
                        help=(f'Set if GeoTiffs in EPSG:4326 should be '
                              f'created for newly downloaded files.'))

    args = parser.parse_args()

    if args.directory == os.getcwd():
        if args.yes:
            print(f"Do you really want to store RADOLAN data in "
                  f"\"{os.getcwd()}\"?")
            do = input("[y/N] ")
            if do in valid_y:
                pass
            elif do in valid_n:
                raise Exception("User interruption.")

    assert args.errors < 21, \
        "Error value too high. Please be respectful with the data provider."

    successfull_down = radolan_down(rad_dir_dwd=args.url,
                                    rad_dir=args.directory,
                                    errors_allowed=int(args.errors),
                                    start_date=args.start,
                                    end_date=args.end)
    if len(successfull_down) > 0:
        if args.sort:
            # sort_tars.sort_tars(path=args.directory)
            new_paths = sort_tars.sort_tars(files=successfull_down)
        # TODO only untar successfull_down files
        if args.extract:
            untarred_dirs = untar.untar(files=new_paths)
        if args.geotiff and (all([d is not None for d in untarred_dirs])):
            tiff_dir = try_create_directory(os.path.join(args.directory,
                                                         "tiff"))
            asc_files = get_asc_files(untarred_dirs)
            create_geotiffs(asc_files, tiff_dir)
        else:
            print("Cannot create GeoTiffs - no newly extracted *.asc files.")


if __name__ == "__main__":
    main()
