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
import time
from datetime import datetime


def untar(path):

    os.chdir(path)

    print("\n"+str(datetime.now())[:-4] + '   getting filenames...')
    count_tarred = 0
    count_to_tar = 0
    count_not_tarred = 0
    fileSet = []
    for dir_, _, files in os.walk(path):
        for fileName in files:

            if (re.match(r".+\.tar$", fileName) is not None
                    or re.match(r".+\.tar\.gz$", fileName) is not None):
                os.chdir(dir_)
                relDir = os.path.relpath(dir_, path)
                relFile = os.path.join(relDir, fileName)
                os.chdir(dir_)
                if os.path.exists(fileName.split(".")[0]) is not True:
                    fileSet.append(relFile)
                    count_to_tar += 1
                else:
                    # print(fileName, " skipped. Filename already exists.",
                    #       end="\n")
                    count_not_tarred += 1
                os.chdir(path)

    # List filenames and ask for deletion
    start = time.time()
    if len(fileSet) != 0:
        # print("\n")
        for f in fileSet:
            tar = tarfile.open(f, 'r')
            print("untarring ", f, end=" ")
            if f[0] == ".":
                i = 1
                tar.extractall(path=f.split(".")[i][1:])
                print("to {}".format(f.split(".")[i][1:]))
            else:
                i = 0
                tar.extractall(path=f.split(".")[i])
                print("to {}".format(f.split(".")[i]))

            tar.close()
            count_tarred += 1
    else:
        print(str(datetime.now())[:-4] + "   no matching files found.")

    end = time.time()
    print("\n" + str(datetime.now())[:-4],
          '  Untarred {} archives in: {:.3f}s'
          .format(count_tarred, end-start),
          "\n                         {} archive(s) skipped"
          .format(count_not_tarred))


def main():
    # TODO add argparse
    untar(os.getcwd())


if __name__ == '__main__':
    main()
