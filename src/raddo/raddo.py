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
import datetime
import argparse

from dateutil.parser import parse
from urllib.request import urlretrieve

from raddo import sort_tars
from raddo import untar
from raddo import __version__

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


rad_dir_dwd = ("https://opendata.dwd.de/climate_environment/CDC/"
               "grids_germany/hourly/radolan/recent/asc/")
rad_dir = os.getcwd()
start_date = "2019-01-01"
end_date = datetime.datetime.today()
errors_allowed = 5
valid_y = ["y", "Y"]
valid_n = ["n", "N", ""]


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
            parsable date string (defaults to current date)

        errors_allowed: integer
            number of tries to download one file (default: 50)

    """
    # Set dates
    if end_date == "today":
        end_datetime = datetime.datetime.today()
    elif type(end_date) == datetime.datetime:
        end_datetime = end_date
    else:
        end_datetime = parse(end_date)

    start_datetime = parse(start_date)

    os.chdir(rad_dir)
    print("\n--------------------------------------------------------------")
    print(f"[LOCAL]  Radolan directory is set to:\n{rad_dir}\n")
    print(f"[REMOTE] Radolan directory is set to:\n{rad_dir_dwd}\n")
    print(f"searching for data from {start_datetime.date()} - "
          f"{end_datetime.date()}.")
    print("\n--------------------------------------------------------------")

    cwd = os.getcwd()

    fileSet = []
    dates_exist = []
    print(str(datetime.datetime.now())[:-4],
          "   getting names of local files in directory:")

    # Get filenames
    for dir_, _, files in os.walk(cwd):
        print(f"                          ...{dir_[-30:]}          \r", end="")
        for fileName in files:
            pattern = r"RW-\d{8}\.tar\.gz$"
            if re.match(pattern, fileName) is not None:
                fileSet.append(fileName)
                dates_exist.append(int(fileName[3:11]))

    print()
    print(str(datetime.datetime.now())[:-4],
          f"   {len(dates_exist)} local archive(s) found.\n")

    # create list of possibly available DATA
    date_list = [start_datetime + datetime.timedelta(days=x)
                 for x in range(int((end_datetime - start_datetime).days))]
    list_DWD = ["RW-{}.tar.gz"
                .format(datetime.datetime.strftime(x, format="%Y%m%d"))
                for x in date_list]

    # Compare local and remote list
    missing_files = []
    for f in list_DWD:
        if f not in fileSet:
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
    else:
        print(str(datetime.datetime.now())[:-4], "   No files missing.\n")

    # try to download all missing files
    for f in missing_files:
        error_count = 0
        while error_count < errors_allowed + 1:
            try:
                print(str(datetime.datetime.now())[:-4],
                      "   [{}] trying {}{}"
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
                    break
                print(str(datetime.datetime.now())[:-4],
                      "   [SUCCESS] {} downloaded.\n".format(f))
                break
            except Exception as e:
                print(str(datetime.datetime.now())[:-4],
                      "   [ERROR] {}\n".format(e))
                error_count += 1
            if error_count is errors_allowed:
                print("\n", str(datetime.datetime.now())[:-4],
                      "   [ERROR!!] Tried {} times to download {}!"
                      .format(error_count, f))


def main():

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        description=('Utility to download RADOLAN data from DWD servers.'),
        prog="radolan_down.py",
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
                              f'be (and may already be) saved.'
                              f'\nDefault: {os.getcwd()}'))
    parser.add_argument('-s', '--start',
                        required=False,
                        default=start_date,
                        action='store', dest='start',
                        help=(f'Start date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {start_date}'))
    parser.add_argument('-e', '--end',
                        required=False,
                        default=end_date,
                        action='store', dest='end',
                        help=(f'End date as parsable string '
                              f'(e.g. "2018-05-20").'
                              f'\nDefault: {end_date}'))
    parser.add_argument('-r', '--Errors-allowed',
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
                        action='store_true', dest='sort',
                        help=(f'Should the data be extracted?'))

    args = parser.parse_args()
    if args.directory == os.getcwd():
        print(f"Do you really want to store RADOLAN data in "
              f"\"{os.getcwd()}\"?")
        do = input("[y/N] ")
        if do in valid_y:
            pass
        elif do in valid_n:
            raise Exception("User interruption.")

    assert args.errors < 21, \
        "Error value too high. Please be respectful with the data provider."

    radolan_down(rad_dir_dwd=args.url,
                 rad_dir=args.directory,
                 errors_allowed=int(args.errors),
                 start_date=args.start,
                 end_date=args.end)
    if args.sort:
        sort_tars(path=args.directory)
    if args.extract:
        untar(path=args.directory)


if __name__ == "__main__":
    main()
