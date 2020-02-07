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
            return f_base
        else:
            print(str(datetime.now())[:-4] + f"   {f_base} already unpacked.")


    count_to_tar = 0
    if not files:
        files = glob.glob("**/*.tar*", recursive=True)

    if path:
        os.chdir(path)
        files = glob.glob("**/*.tar*", recursive=True)
        print('\n'+str(datetime.now())[:-4] + \
              '   getting name of files to untar...')

    ret = []

    if any([f is not None for f in files]):
        for filename in files:
            if filename is None:
                continue
            curdir = os.getcwd()
            root = os.path.dirname(os.path.abspath(filename))
            os.chdir(root)
            filename = os.path.basename(filename)

            f_base = filename.split(".")[0]
            if re.match(r".+\.tar\.gz$", filename) is not None:
                untarred_file = save_untar(filename)
                if untarred_file is not None:
                    ret.append(os.path.join(root, untarred_file))
                    count_to_tar += 1

            if re.match(r".+\.tar$", filename) is not None:
                untarred_file = save_untar(filename)
                if untarred_file is not None:
                    ret.append(os.path.join(root, untarred_file))
                    count_to_tar += 1
                if len(ret) == 0:
                    for gz_root, gz_dirs, gz_files in os.walk(f_base):
                        for gz_filename in gz_files:
                            os.chdir(os.path.join(root, gz_root))
                            f_base = os.path.splitext(gz_filename)[0]
                            if re.match(r".+\.tar.gz$",
                                        gz_filename) is not None:
                                untarred_file = save_untar(filename)
                                if untarred_file is not None:
                                    ret.append(
                                        os.path.join(root,
                                                     untarred_file))
                                    count_to_tar += 1
            os.chdir(curdir)
        print(str(datetime.now())[:-4] + "   done.")
        return ret

    if count_to_tar == 0:
        print(str(datetime.now())[:-4] + "   no matching files found.")
        return ret


def main():
    # TODO add argparse
    untar(os.getcwd())


if __name__ == '__main__':
    main()
