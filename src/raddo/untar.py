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
import os
import sys
import re
import glob
import tarfile
from datetime import datetime


# TODO add *args to accept list of file names
def untar(**kwargs):

    sys.stdout.write("\n"+str(datetime.now())[:-4] +
                     '   started untarring of files..\n')

    path = kwargs.get('path', None)
    files = kwargs.get('files', None)
    assert (path is not None) or (files is not None), \
        "Please either specify a path or filelist to untar."

    def save_untar(filename):
        "untar file into directory named after basename of file."
        f_base = filename.split(".")[0]
        if os.path.exists(f_base):
            dir_is_empty = (len(os.listdir(f_base)) == 0)
        else:
            dir_is_empty = False
        if not os.path.exists(f_base) or dir_is_empty:
            tar = tarfile.open(filename, 'r')
            sys.stdout.write('\r' + str(datetime.now())[:-4] + "   " +
                             f"untarring {filename} to {f_base}.")
            tar.extractall(path=f_base)
            tar.close()
            del tar
            return f_base
        else:
            sys.stdout.write('\r' + str(datetime.now())[:-4] +
                             f"   {f_base} already unpacked.")
            return f_base

    count_to_tar = 0
    if not files:
        files = glob.glob("**/*.tar*", recursive=True)

    if path:
        os.chdir(path)
        files = glob.glob("**/*.tar*", recursive=True)
        sys.stdout.write('\n'+str(datetime.now())[:-4] +
                         '   getting name of files to untar...\n')

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
                    del untarred_file
                    count_to_tar += 1

            if re.match(r".+\.tar$", filename) is not None:
                untarred_file = save_untar(filename)
                if untarred_file is not None:
                    ret.append(os.path.join(root, untarred_file))
                    del untarred_file
                    count_to_tar += 1
                # if len(ret) == 0:
                    for gz_root, gz_dirs, gz_files in os.walk(f_base):
                        for gz_filename in gz_files:
                            os.chdir(os.path.join(root, gz_root))
                            f_base = os.path.splitext(gz_filename)[0]
                            if re.match(r".+\.tar.gz$",
                                        gz_filename) is not None:
                                untarred_file = save_untar(gz_filename)
                                if untarred_file is not None:
                                    ret.append(
                                        os.path.join(root,
                                                     untarred_file))
                                    del untarred_file
                                    count_to_tar += 1
            os.chdir(curdir)
        sys.stdout.write("\n" + str(datetime.now())[:-4] + "   done.\n")
        return ret

    if count_to_tar == 0:
        sys.stderr.write(str(datetime.now())[:-4] +
                         "   no matching files found.\n")
        return ret


def main():
    # TODO add argparse
    untar(os.getcwd())


if __name__ == '__main__':
    main()
