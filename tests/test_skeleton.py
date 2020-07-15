# -*- coding: utf-8 -*-

import pytest
import datetime
import os
from raddo import *
import tempfile
from raddo import sort_tars
from raddo import untar

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"

RAD_DIR_DWD = ("https://opendata.dwd.de/climate_environment/CDC/"
               "grids_germany/hourly/radolan/recent/asc/")
RAD_DIR_DWD_HIST = ("https://opendata.dwd.de/climate_environment/CDC/"
                    "grids_germany/hourly/radolan/historical/asc/")

FILELIST = ".raddo_local_files.txt"
START_DATE = f"{datetime.datetime.today().year}-01-01"
END_DATE = datetime.datetime.today() - datetime.timedelta(1)  # Yesterday
END_DATE_STR = datetime.datetime.strftime(END_DATE, "%Y-%m-%d")
ERRORS_ALLOWED = 5
VALID_Y = ["y", "Y"]
VALID_N = ["n", "N", ""]

DWD_PROJ = ("+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 "
            "+a=6370040 +b=6370040 +units=m")


def test_raddo_complete_download():
    START_DATE = datetime.datetime.today() - datetime.timedelta(4)  # Yesterday
    END_DATE = datetime.datetime.today() - datetime.timedelta(2)  # Yesterday
    with tempfile.TemporaryDirectory() as tmpdirname:
        RAD_DIR = tmpdirname
        tiff_dir = try_create_directory(os.path.join(RAD_DIR,
                                                           "tiff"))
        successfull_down = radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                              rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                              rad_dir=RAD_DIR,
                                              errors_allowed=ERRORS_ALLOWED,
                                              start_date=START_DATE,
                                              end_date=END_DATE,
                                              force=True,
                                              force_down=True)

        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        asc_files = get_asc_files(untarred_dirs)
        gtiff_files = create_geotiffs(asc_files, tiff_dir)
        create_netcdf(gtiff_files, RAD_DIR)
