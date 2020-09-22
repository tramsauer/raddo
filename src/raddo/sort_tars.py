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


def sort_tars(**kwargs):
    sys.stdout.write("\n"+str(datetime.now())[:-4] +
                     "   started sorting of files..\n")
    fileSet = glob.glob('*.tar*')

    path = kwargs.get('path', None)
    files = kwargs.get('files', None)
    assert (path is not None) or (files is not None), \
        "Please either specify a path or filelist to untar."

    if path:
        os.chdir(path)
        sys.stdout.write("\n"+str(datetime.now())[:-4] +
                         "   getting filenames in {path}..\n")
        fileSet = glob.glob('*.tar*')
    else:
        fileSet = files

    if len(fileSet) == 0:
        sys.stdout.write('No files found.\n')
    else:
        new_paths = []
        for file in fileSet:
            year = file[3:7]
            if not os.path.splitext(file)[-1] == ".tar":
                month = file[7:9]
                future_file_path = './{}/RW-{}{}'.format(year, year, month)
            else:
                month = ""
                future_file_path = './{}/'.format(year)
            # print(future_file_path)
            try:
                # TODO: replace os.system
                os.system('mkdir -vp {}'.format(future_file_path))
                os.system('mv -v {} {}'.format(file, future_file_path))
                new_paths.append(os.path.join(future_file_path, file))
            except Exception:
                sys.stderr.write('ERROR.\n')

    sys.stdout.write(str(datetime.now())[:-4] + '  Sorting finished.\n')
    return new_paths


def main():
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('[ERROR]: %s\n' % message)
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
