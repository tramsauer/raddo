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
import glob
import tarfile
from datetime import datetime


# TODO add *args to accept list of file names
def untar(**kwargs):

    print("\n"+str(datetime.now())[:-4] + f'   started untarring of files..')

    path = kwargs.get('path', None)
    files = kwargs.get('files', None)
    assert (path is not None) or (files is not None), \
        "Please either specify a path or filelist to untar."


    def save_untar(filename):
        "untar file into directory named after basename of file."
        f_base = filename.split(".")[0]
        if not os.path.exists(f_base):
            tar = tarfile.open(filename, 'r')
            print(str(datetime.now())[:-4] + "   ", end="")
            print("untarring ", filename, end=" ")
            print("to {}".format(f_base))
            tar.extractall(path=f_base)
            return 0
        return 1

    count_to_tar = 0
    if not files:
        files = glob.glob("**/*.tar*", recursive=True)

    if path:
        os.chdir(path)
        files = glob.glob("**/*.tar*", recursive=True)
        print('\n'+str(datetime.now())[:-4] + \
              '   getting name of files to untar...')


    for filename in files:
        root = os.path.relpath(os.path.dirname(filename))
        os.chdir(root)
        filename = os.path.basename(filename)

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
