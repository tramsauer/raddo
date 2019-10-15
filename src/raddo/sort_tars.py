#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    sort downloaded RADOLAN tar.gz files, according to year, month, ..
"""

import glob
import os
import sys
import argparse

from datetime import datetime


__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"


def sort_tars(path):
    os.chdir(path)
    print("\n"+str(datetime.now())[:-4] + f'   getting filenames in {path}..')
    fileSet = glob.glob('*.tar.gz')

    if len(fileSet) == 0:
        print('No files found.')
    else:
        for file in fileSet:
            year = file[3:7]
            month = file[7:9]
            future_file_path = './{}/RW-{}{}'.format(year, year, month)
            # print(future_file_path)
            try:
                os.system('mkdir -vp {}'.format(future_file_path))
                os.system('mv -v {} {}'.format(file, future_file_path))
            except Exception:
                print('ERROR.')
    print("\n" + str(datetime.now())[:-4], 'Sorting finished.')


def main():
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(
        description=('Utility to sort downloaded RADOLAN tar.gz files, '
                     'in subdirectories according to year, month '
                     '(e.g. ./2018/RW-201810/)'),
        prog="sort_tars.py",
        # usage='%(prog)s directory [-h] [-p]'
        )
    parser.add_argument('-d', '--directory',
                        required=False,
                        default=f"{os.getcwd()}",
                        action='store', dest='directory',
                        help=(f'Path to local directory where RADOLAN .tar.gz'
                              f'files are saved.'
                              f'\nDefault: {os.getcwd()}'))
    args = parser.parse_args()

    sort_tars(path=args.directory)


if __name__ == '__main__':
    main()
