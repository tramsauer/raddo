# -*- coding: utf-8 -*-

import pytest
import datetime
import os
import tempfile

import sys
sys.path.append(os.path.join(os.path.dirname(__file__),os.pardir,"src"))
from raddo import sort_tars
from raddo import untar
from raddo.raddo import Raddo

__author__ = "Thomas Ramsauer"
__copyright__ = "Thomas Ramsauer"
__license__ = "gpl3"

RAD_DIR_DWD = ("https://opendata.dwd.de/climate_environment/CDC/"
               "grids_germany/hourly/radolan/recent/asc/")
RAD_DIR_DWD_HIST = ("https://opendata.dwd.de/climate_environment/CDC/"
                    "grids_germany/hourly/radolan/historical/asc/")

FILELIST = ".raddo_local_files.txt"
START_DATE = f"{datetime.datetime.today().year}-01-01"
END_DATE = datetime.datetime.today().date() - datetime.timedelta(days=1)  # Yesterday
END_DATE_STR = datetime.datetime.strftime(END_DATE, "%Y-%m-%d")
ERRORS_ALLOWED = 5
VALID_Y = ["y", "Y"]
VALID_N = ["n", "N", ""]

DWD_PROJ = ("+proj=stere +lon_0=10.0 +lat_0=90.0 +lat_ts=60.0 "
            "+a=6370040 +b=6370040 +units=m")


def _date_str(ds):
    return datetime.datetime.strftime(ds, "%Y-%m-%d")


def test_property_list_of_files():
    print(Raddo.list_of_available_files)


def test_local_file_list():
    rd = Raddo()
    print(rd.local_file_list_exists())

def test_mask_pts():
    rd = Raddo()
    maskfile = os.path.join(os.path.dirname(__file__),
                            "shps/test_pts.shp")
    print(maskfile)
    rd.read_mask(maskfile)

def test_mask_poly():
    rd = Raddo()
    maskfile = os.path.join(os.path.dirname(__file__),
                            "shps/test_poly.shp")
    print(maskfile)
    rd.read_mask(maskfile)

def test_mask_poly_multi():
    rd = Raddo()
    maskfile = os.path.join(os.path.dirname(__file__),
                            "shps/test_poly_multi.shp")
    print(maskfile)
    rd.read_mask(maskfile)


def test_trycreatedir():
    with tempfile.TemporaryDirectory() as tdir:
        print(Raddo.try_create_directory(tdir))


def test_raddo_complete_download():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=4),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date() - datetime.timedelta(days=2))  # Yesterday
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        RAD_DIR = tmpdirname
        rd = Raddo()
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                              rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                              rad_dir=RAD_DIR,
                                              errors_allowed=ERRORS_ALLOWED,
                                              start_date=START_DATE,
                                              end_date=END_DATE,
                                              force=True,
                                              force_down=True)

        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        asc_files = rd.get_asc_files(untarred_dirs)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        rd.create_netcdf(gtiff_files, RAD_DIR)
    tempfile.TemporaryDirectory().cleanup()


def test_raddo_complete_download_old():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=400),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date()
                         - datetime.timedelta(days=399))
    print(START_DATE, END_DATE)
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        RAD_DIR = tmpdirname
        rd = Raddo()
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                              rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                              rad_dir=RAD_DIR,
                                              errors_allowed=ERRORS_ALLOWED,
                                              start_date=START_DATE,
                                              end_date=END_DATE,
                                              force=True,
                                              force_down=True)

        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        print(untarred_dirs)
        asc_files = rd.get_asc_files(untarred_dirs)
        print(asc_files)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        print(gtiff_files)
        rd.create_netcdf(gtiff_files, RAD_DIR)
    tempfile.TemporaryDirectory().cleanup()


def test_raddo_complete_download_with_mask_pts():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=4),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date()
                         - datetime.timedelta(days=2))  # Yesterday

    tempfile.TemporaryDirectory().cleanup()
    with tempfile.TemporaryDirectory(suffix="pts") as tmpdirname:
        print(tmpdirname)
        os.chdir(tmpdirname)
        rd = Raddo()
        RAD_DIR = tmpdirname
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        maskfile = os.path.join(os.path.dirname(__file__),
                                "shps/test_pts.shp")
        print(maskfile)
        rd.read_mask(maskfile)
        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                           rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                           rad_dir=RAD_DIR,
                                           errors_allowed=ERRORS_ALLOWED,
                                           start_date=START_DATE,
                                           end_date=END_DATE,
                                           force=True,
                                           force_down=True)

        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        asc_files = rd.get_asc_files(untarred_dirs)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        rd.create_netcdf(gtiff_files, RAD_DIR)


def test_raddo_complete_download_with_mask_poly():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=4),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date() -
                         datetime.timedelta(days=2))  # Yesterday

    tempfile.TemporaryDirectory().cleanup()
    with tempfile.TemporaryDirectory(suffix="pts") as tmpdirname:
        print(tmpdirname)
        os.chdir(tmpdirname)
        rd = Raddo()
        RAD_DIR = tmpdirname
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        maskfile = os.path.join(os.path.dirname(__file__),
                                "shps/test_poly.shp")
        print(maskfile)
        rd.read_mask(maskfile)
        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                              rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                              rad_dir=RAD_DIR,
                                              errors_allowed=ERRORS_ALLOWED,
                                              start_date=START_DATE,
                                              end_date=END_DATE,
                                              force=True,
                                              force_down=True)

        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        asc_files = rd.get_asc_files(untarred_dirs)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        rd.create_netcdf(gtiff_files, RAD_DIR)


def test_raddo_complete_download_with_mask_poly_multi():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=4),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date()
                         - datetime.timedelta(days=2))  # Yesterday

    tempfile.TemporaryDirectory().cleanup()
    with tempfile.TemporaryDirectory(suffix="pts") as tmpdirname:
        print(tmpdirname)
        os.chdir(tmpdirname)
        rd = Raddo()
        RAD_DIR = tmpdirname
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                              rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                              rad_dir=RAD_DIR,
                                              errors_allowed=ERRORS_ALLOWED,
                                              start_date=START_DATE,
                                              end_date=END_DATE,
                                              force=True,
                                              force_down=True)


        ## POLY MULT
        maskfile = os.path.join(os.path.dirname(__file__),
                                "shps/test_poly_multi.shp")
        print(maskfile)
        rd.read_mask(maskfile)
        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                     "tiff"))
        asc_files = rd.get_asc_files(untarred_dirs)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        rd.create_netcdf(gtiff_files, RAD_DIR)


        # ## POLY
        # maskfile = os.path.join(os.path.dirname(__file__),
        #                         "shps/test_poly.shp")
        # print(maskfile)
        # rd.read_mask(maskfile)
        # new_paths = sort_tars.sort_tars(files=successfull_down)
        # untarred_dirs = untar.untar(files=new_paths)
        # tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
        #                                              "tiff"))
        # asc_files = rd.get_asc_files(untarred_dirs)
        # gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        # rd.create_netcdf(gtiff_files, RAD_DIR)

        # ## PTS
        # maskfile = os.path.join(os.path.dirname(__file__),
        #                         "shps/test_pts.shp")
        # print(maskfile)
        # rd.read_mask(maskfile)
        # new_paths = sort_tars.sort_tars(files=successfull_down)
        # untarred_dirs = untar.untar(files=new_paths)
        # tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
        #                                              "tiff"))
        # asc_files = rd.get_asc_files(untarred_dirs)
        # gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        # rd.create_netcdf(gtiff_files, RAD_DIR)

def test_raddo_complete_download_with_point():
    START_DATE = datetime.datetime.strftime(
        datetime.datetime.today().date() - datetime.timedelta(days=4),
        "%Y-%m-%d")
    END_DATE = _date_str(datetime.datetime.today().date()
                         - datetime.timedelta(days=2))  # Yesterday

    tempfile.TemporaryDirectory().cleanup()
    with tempfile.TemporaryDirectory(suffix="point") as tmpdirname:
        print(tmpdirname)
        os.chdir(tmpdirname)
        rd = Raddo()
        RAD_DIR = tmpdirname
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))

        successfull_down = rd.radolan_down(rad_dir_dwd=RAD_DIR_DWD,
                                                rad_dir_dwd_hist=RAD_DIR_DWD_HIST,
                                                rad_dir=RAD_DIR,
                                                errors_allowed=ERRORS_ALLOWED,
                                                start_date=START_DATE,
                                                end_date=END_DATE,
                                                force=True,
                                                force_down=True)


        new_paths = sort_tars.sort_tars(files=successfull_down)
        untarred_dirs = untar.untar(files=new_paths)
        tiff_dir = rd.try_create_directory(os.path.join(RAD_DIR,
                                                        "tiff"))
        asc_files = rd.get_asc_files(untarred_dirs)
        gtiff_files = rd.create_geotiffs(asc_files, tiff_dir)
        rd.create_netcdf(gtiff_files, RAD_DIR)
        print("NetCDF file name (rd.netcdf_file_name):" + rd.netcdf_file_name)
        rd.read_coords("12,48")
        rd.create_point_from_netcdf()
