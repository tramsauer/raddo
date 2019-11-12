#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

UNTAR all in here - in place!
==============================

Archives (.tar & .tar.gz) are untarred/extracted recursively from entered
path on into folders with their names.
If folder to be created exists (regardless of content),
archive is skipped.

"""
from __future__ import print_function

import os
import re
import tarfile
from datetime import datetime


# TODO add *args to accept list of file names
def untar(path):

    os.chdir(path)

    print('\n'+str(datetime.now())[:-4] + \
          '   getting name of files to untar...')
    count_to_tar = 0

    def save_untar(filename):
        f_base = filename.split(".")[0]
        if not os.path.exists(f_base):
            tar = tarfile.open(filename, 'r')
            print(str(datetime.now())[:-4] + "   ", end="")
            print("untarring ", filename, end=" ")
            print("to {}".format(f_base))
            tar.extractall(path=f_base)
            return 0
        return 1

    for root, dirs, files in os.walk(path):
        for filename in files:
            os.chdir(root)
            f_base = filename.split(".")[0]
            if re.match(r".+\.tar\.gz$", filename) is not None:
                count_to_tar += 1
                save_untar(filename)
            if re.match(r".+\.tar$", filename) is not None:
                count_to_tar += 1
                ret = save_untar(filename)
                if ret == 0:
                    for gz_root, gz_dirs, gz_files in os.walk(f_base):
                        for gz_filename in gz_files:
                            os.chdir(os.path.join(root, gz_root))
                            f_base = os.path.splitext(gz_filename)[0]
                            if re.match(r".+\.tar.gz$", gz_filename) is not None:
                                count_to_tar += 1
                                save_untar(gz_filename)

    if count_to_tar == 0:
        print(str(datetime.now())[:-4] + "   no matching files found.")
    else:
        print(str(datetime.now())[:-4] + "   done.")


def main():
    # TODO add argparse
    untar(os.getcwd())


if __name__ == '__main__':
    main()
