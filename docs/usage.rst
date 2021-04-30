.. _usage:

==============
Usage
==============


Download RADOLAN data from *{current-year}-01-01* till *today* to
current directory with ``raddo``. For further arguments consult the help
text:

.. code:: sh
    usage: raddo [-h] [-s START] [-e END] [-d DIRECTORY] [-C] [-f] [-x] [-g] [-n]
                 [-N OUTFILE] [-m MASK] [-b BUFFERSIZE] [-F] [-D] [-y] [-v]
                 [-u URL] [-r ERRORS] [-t]

    raddo - utility to download RADOLAN data from DWD servers and prepare for
    simple usage.

    optional arguments:
      -h, --help            show this help message and exit
      -s START, --start START
                            Start date as parsable string (e.g. "2018-05-20").
                            Default: 14 days ago.
      -e END, --end END     End date as parsable string (e.g. "2020-05-20").
                            Default: yesterday.
      -d DIRECTORY, --directory DIRECTORY
                            Absolute path to local directory where RADOLAN data
                            should be (and may already be) saved. Checks for
                            existing files only if this flag is set. Default:
                            /home/tom/Code/raddo (current directory)
      -C, --complete        Run all subcommands. Same as using flags -fxgn.
      -f, --sort-in-folders
                            Should the data be sorted in folders?
      -x, --extract         Should the data be extracted?
      -g, --geotiff         Set if GeoTiffs in EPSG:4326 should be created for
                            newly downloaded files.
      -n, --netcdf          Create a NetCDF from GeoTiffs?
      -N OUTFILE, --netcdf-file OUTFILE
                            Name of the output NetCDF file.
      -m MASK, --mask MASK  Use mask when creating NetCDF.
      -b BUFFERSIZE, --buffer BUFFERSIZE
                            Buffer in meter around mask shapefile (Default 1400m).
      -F, --force           Forces local file search. Omits faster check of
                            ".raddo_local_files.txt".
      -D, --force-download  Forces download of all files.
      -y, --yes             Skip user input. Just accept to download to current
                            directory if not specified otherwise.
      -v, --version         Print information on software version.
      -u URL, --radolan_server_url URL
                            Path to recent .asc RADOLAN data on DWD servers.
                            Default: https://opendata.dwd.de/climate_environment/C
                            DC/grids_germany/hourly/radolan/recent/asc/
      -r ERRORS, --errors-allowed ERRORS
                            Errors allowed when contacting DWD Server. Default: 5
      -t, --no-time-correction
                            Omit time adjustment to previous hour in netCDF file
                            creation and just use RADOLANs sum up time HH:50
                            (Default: false).



Example
~~~~~~~

Download `RADOLAN` data to *folder1* (`-d`) from *2020-07-15* (`-s`) until yesterday (default) for point in shapefile `test_pt.shp` (`-m`). Sort and extract nested archives and create GeoTiffs and a single NetCDF file from there (`-C`). Don't check for available files but just download all needed files (`-D`):

.. code:: sh

   raddo -d "folder1" -s "2020-07-15" -CD -m "test_pt.shp"

More visual:

.. figure:: raddo.gif
   :alt: Terminal prompt

   example image should load here…


Warnings
--------

-  currently, if a shapefile mask is used, sub-optimal *nearest
   neighbour resampling* is applied in the GeoTiff conversion (as other
   methods were not functional in gdal python bindings..(?)).
-  if GeoTiffs are not wanted, they need to be created anyways, and
   processing might fill up your *tempfs* in ``/tmp``..
-  if multiple polygons are used as mask, they are dissolved & buffered.
-  ``raddo`` does not recreate nor warn if GeoTiffs are already
   available.



Crontab
~~~~~~~

.. note::
   This part is outdated:

An entry in crontab could be used to download/mirror the data. E.g.:

.. code:: bash

   0 12 * * 1-5 raddo -fx -d /path/to/radolan/data/

The following skript (Anaconda is used as python *distribution*) can be used to log

.. code:: sh

   #!/usr/bin/env bash
   export PATH="$HOME/.anaconda3/bin:$PATH"
   DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
   date=$(date)
   header="\n--------------------------\n"$date" executing raddo:\n"
   echo -e $header >> $DIR"/raddo.log"
   python ~/path/to/raddo/raddo.py &>> $DIR"/raddo.log"

This adds the anaconda path to the ``$PATH`` variable. Furthermore, it
uses the directory which the shell script is executed from as ``$DIR``
to write/append the ``$header``\ and ``stdout`` to a custom log file
(``raddo.log``).


Python script
~~~~~~~~~~~~~

.. code:: python

   import raddo as rd

   rd.radolan_down(rad_dir_dwd = ...,  )

Variables and their defaults are:

::

      PARAMETERS:
      -------------------------
          rad_dir_dwd: string
              Link to Radolan products on DWD FTP server.
              defaults to "https://opendata.dwd.de/climate_environment/CDC/
                           grids_germany/hourly/radolan/recent/asc/")

          rad_dir_dwd_hist: string
              Link to Radolan products on DWD FTP server.
              defaults to "https://opendata.dwd.de/climate_environment/CDC/"
                          "grids_germany/hourly/radolan/historical/asc/"

          rad_dir: string
              local directory to be processed / already containing radolan data.
              defaults to current working directory

          start_date: string
              parsable date string (default: 14 days ago)

          end_date: string
              parsable date string (default: yesterday)

          errors_allowed: integer
              number of tries to download one file (default: 5)

          force:
              Forces local file search. Omits faster check of
              .raddo_local_files.txt".

          force_down:
              Forces download of all files.

          mask:
              Mask shapefile.

          buffer:
              Buffer in meter around shapefile mask.
