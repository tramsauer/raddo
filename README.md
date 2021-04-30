**raddo**: A Python Package for RADOLAN Weather Radar Data Provision

[![license badge](https://img.shields.io/badge/license-GNU_GPLv3-blue)](LICENSE.txt)
<!-- [![Docker Build Status](https://img.shields.io/docker/cloud/build/tramsauer/raddo?logo=docker)](https://hub.docker.com/r/tramsauer/raddo/) -->
<!-- [![GitHub release](https://img.shields.io/github/release/RaT0M/raddo.svg?logo=github)](https://github.com/RaT0M/raddo/releases/latest)  -->

*raddo* helps you find, download, sort and preprocess RADOLAN weather radar precipitation data for further usage.


- [Installation](#Installation)
  - [GDAL](#GDAL)
  - [Direct Install](#DirectInstall)
- [Usage](#Usage)
  - [CLI Example](#CLIExample)
  - [Crontab](#Crontab)
  - [Python Script](#PythonScript)
  - [Docker](#Docker)
  - [Warnings](#Warnings)
- [Contributing](#Contributing)
- [License](#License)
- [Changelog](#Changelog)
- [Further Development](#FurtherDevelopment)
- [See also](#Seealso)

*raddo* downloads and processes RADOLAN weather radar ASCII data.
Downloaded files are sorted in folders based on year and month and may also be decompressed.
As next step *raddo* creates GeoTiffs in generic WGS84 lat/lon coordinates and/or a single NetCDF file upon user request.
In case the data is only needed for a smaller region, masking via a shapefile is also possible.
For all possibilities on data retrieval and processing see the *usage section*.

*raddo* tries to download all recent RADOLAN ASCII files / archives from the DWD FTP server to the specified directory if files do not exist already. A list of dates possibly available (default \<current year\>-01-01 until today) is used to compare hypothetical available data sets with actual local available ones. So file listing on the FTP side is skipped due to (formerly) unreliable connection.

RADOLAN data from the German Weather Service (Deutscher Wetterdienst, DWD) is copyrighted! Please find the copyright text [here](https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf).
The freely accessible data may be re-used without any restrictions provided that the source reference is indicated, as laid down in the GeoNutzV ordinance.

The RADOLAN precipitation data files are *updated daily* by DWD.

<img align="right" src="dwd_logo.png" width="200">

The data can be found at [opendata.dwd.de](https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/ "https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/").


## Installation <a name="Installation"></a>

The software is developed and tested for usage in Linux.
The preferred way of installing is in a `conda` environment because a working GDAL install is more likely with this option.
A conda package for raddo will potentially be available in the future through `conda forge`.
However, also direct installation is possible. A `pip` package is however not provided for that reasons.
Testing is done using the conda version of GDAL with `pytest`.

There is also a docker image available at the [docker hub](https://hub.docker.com/r/tramsauer/raddo/) if you don't mind the overhead. See the docker section below for instructions.

### GDAL <a name="GDAL"></a>

`GDAL` is a requirement of `raddo`.
Installation of this dependency can be a problem.
If errors arise, `GDAL` binaries might be missing.
When using *conda*, `conda install -c conda-forge gdal` should work.
On Ubuntu (and derivates) using the `UbuntuGIS-ppa` seems to be working quite well.

<!-- ### `conda` Install -->

<!-- not yet: -->
<!-- ```sh -->
<!-- conda install -c conda-forge raddo -->
<!-- ``` -->

### Direct Install <a name="DirectInstall"></a>

Better have GDAL python bindings already installed (see above).
Clone this repository, change into new directory and run:

``` sh
git clone <repo-url>
cd raddo
pip install .
```

or
``` sh
pip install -e .
```
if you want to work on the code.


## Usage <a name="Usage"></a>

Download RADOLAN data from *{current-year}-01-01* till *today* to current directory with `raddo`. For further arguments consult the help text:


``` sh
usage: raddo [-h] [-u URL] [-d DIRECTORY] [-s START] [-e END] [-r ERRORS] [-f]
             [-x] [-g] [-n] [-m MASK] [-b BUFFER] [-C] [-y] [-F] [-D] [-v]

raddo - utility to download RADOLAN data from DWD servers and prepare for
simple usage.

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --radolan_server_url URL
                        Path to recent .asc RADOLAN data on DWD servers.
                        Default: https://opendata.dwd.de/climate_environment/C
                        DC/grids_germany/hourly/radolan/recent/asc/
  -d DIRECTORY, --directory DIRECTORY
                        Path to local directory where RADOLAN shouldbe (and
                        may already be) saved. Checks for existing files only
                        if this flag is set. Default: /home/tom (current
                        directory)
  -s START, --start START
                        Start date as parsable string (e.g. "2018-05-20").
                        Default: 2020-01-01 (current year\'s Jan 1st)
  -e END, --end END     End date as parsable string (e.g. "2020-05-20").
                        Default: 2020-07-16 (yesterday)
  -r ERRORS, --errors-allowed ERRORS
                        Errors allowed when contacting DWD Server. Default: 5
  -f, --sort-in-folders
                        Should the data be sorted in folders?
  -x, --extract         Should the data be extracted?
  -g, --geotiff         Set if GeoTiffs in EPSG:4326 should be created for
                        newly downloaded files.
  -n, --netcdf          Create a NetCDF from GeoTiffs?
  -m MASK, --mask MASK  Use mask when creating NetCDF.
  -b BUFFER, --buffer BUFFER
                        Buffer in meter around mask shapefile (Default 1400m).
  -C, --complete        Run all subcommands. Same as using flags -fxgn.
  -y, --yes             Skip user input. Just accept to download to current
                        directory if not specified otherwise.
  -F, --force           Forces local file search. Omits faster check of
                        ".raddo_local_files.txt".
  -D, --force-download  Forces download of all files.
  -v, --version         Print information on software version.

```
### CLI Example <a name="CLIExample"></a>

Force local available file search, download and processing (sorting, extracting, geotiff & netCDF creation) of `RADOLAN` data for point in shapefile `test_pt.shp` with:
``` sh
raddo -d "/folder1" -s "2020-07-15" -CFD -m "test_pt.shp"
```

More visual:

![example image should load here...](raddo.gif "Terminal prompt")


### Crontab  <a name="Crontab"></a>

An entry in crontab could be used to download the data. E.g.:

``` bash
0 12 * * 1-5 raddo -fx -d /path/to/radolan/data/
```

To have the following skript running every weekday at 12:00 noon.

``` sh
#!/usr/bin/env bash
export PATH="$HOME/.anaconda3/bin:$PATH"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
date=$(date)
header="\n--------------------------\n"$date" executing raddo:\n"
echo -e $header >> $DIR"/raddo.log"
python ~/path/to/raddo/raddo.py &>> $DIR"/raddo.log"
```

This adds the anaconda path to the `$PATH` variable. Furthermore, it uses the
directory which the shell script is executed from as `$DIR` to write/append the
`$header`and `stdout` to a custom log file (`raddo.log`).

``` sh
sort_tars.sh && untar_default.sh
```
may be added to fully extract and sort the downloaded archives.


### Python Script <a name="PythonScript"></a>


``` python
import raddo as rd

rd.radolan_down(rad_dir_dwd = ...,  )
```

 Variables and their defaults are:

 ```
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
            parsable date string (default "2019-01")

        end_date: string
            parsable date string (defaults to current date)

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

 ```

### Docker <a name="Docker"></a>


Docker lets you run raddo in a containerized form.
All depenencies are set up - including GDAL.
`docker pull tramsauer/raddo` gets you the prebuilt image from docker-hub.
Alternatively, with the included `Dockerfile` the image can also be directly built with `docker build -t raddo .` from the root directory of the repository.

`raddo` then can be used like this:

`docker run -ti --rm  -v /tmp/RADOLAN:/data raddo -C -s "20210422"`

- `-ti`: docker runs in an interactive tty
- `--rm`: the container is destroyed after usage
- `-v /tmp/RADOLAN:/data`: an existing folder (`/tmp/RADOLAN`) is connected to the container (internal folder `/data`)
  - If asked accept to save the data in `/data`
- `raddo`: image name, that automatically starts the `raddo` program
- `-C -s ....`: after the image name, additional arguments for `raddo` can be added, here:
  - `-C`: complete processing
  - `-s "20210422"`: starting date

The data can then be found in the linked folder, e.g. `/tmp/RADOLAN`.


### Warnings <a name="Warnings"></a>

- currently, if a shapefile mask is used, sub-optimal *nearest neighbour resampling* is applied in the GeoTiff conversion (as other methods were not functional in gdal python bindings..(?)).
- if GeoTiffs are not wanted, they need to be created anyways, and processing might fill up your *tempfs* in `/tmp`..
- if multiple polygons are used as mask, they are dissolved & buffered.
- `raddo` does not recreate nor warn if GeoTiffs are already available.

## Contributing <a name="Contributing"></a>

See [CONTRIBUTING](CONTRIBUTING.md) document.

## License <a name="License"></a>
[![license badge](https://img.shields.io/badge/license-GNU_GPLv3-blue)](LICENSE.txt)

Please find the license agreement in [LICENSE.txt](LICENSE.txt)

## Changelog <a name="Changelog"></a>

See [Changelog](CHANGELOG.md) document.

## Further Development <a name="FurtherDevelopment"></a>

- [ ] add DOI
- [ ] add conda install

## See also <a name="Seealso"></a>

- [wradlib](https://github.com/wradlib/wradlib):
  > An Open Source Library for Weather Radar Data Processing

- [radproc](https://github.com/jkreklow/radproc):
  > A GIS-compatible Python-Package for automated RADOLAN Composite Processing and Analysis
