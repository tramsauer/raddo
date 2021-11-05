# **raddo**: A Python Package for RADOLAN Weather Radar Data Provision

[![license badge](https://img.shields.io/badge/license-GNU_GPLv3-blue)](LICENSE.txt)
[![Build Status: master](https://travis-ci.com/RaT0M/raddo.svg?branch=main)](https://app.travis-ci.com/github/RaT0M/raddo)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/tramsauer/raddo?logo=docker)](https://hub.docker.com/r/tramsauer/raddo/)
[![GitHub release](https://img.shields.io/github/release/RaT0M/raddo.svg?logo=github)](https://github.com/RaT0M/raddo/releases/latest)
[![Documentation Status](https://readthedocs.org/projects/raddo/badge/?version=stable)](https://raddo.readthedocs.io/en/stable/?badge=stable)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5642650.svg)](https://doi.org/10.5281/zenodo.5642650)

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
- [See also](#Seealso)

*raddo* downloads and processes RADOLAN weather radar ASCII data.
Downloaded files are sorted in folders based on year and month and may also be decompressed.
As next step *raddo* creates GeoTiffs in generic WGS84 lat/lon coordinates and/or a single NetCDF file upon user request.
In case the data is only needed for a smaller region, masking via a shapefile is also possible.
For all possibilities on data retrieval and processing see the *usage section*.

*raddo* tries to download all recent RADOLAN ASCII files / archives from the DWD FTP server to the specified directory if files do not exist already. A list of dates possibly available is used to compare hypothetical available data sets with actual local available ones. So file listing on the FTP side is skipped due to (formerly) unreliable connection.

RADOLAN data from the German Weather Service (Deutscher Wetterdienst, DWD) is copyrighted! Please find the copyright text [here](https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf).
The freely accessible data may be re-used without any restrictions provided that the source reference is indicated, as laid down in the GeoNutzV ordinance.

The RADOLAN precipitation data files are *updated daily* by DWD.

<img align="right" src="dwd_logo.png" width="200">

The data can be found at [opendata.dwd.de](https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/ "https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/").


## Installation <a name="Installation"></a>

The software is developed and tested for usage in Linux.
The preferred way of installing is in a `conda` environment because a working GDAL install is more likely with this option.
A conda package for raddo will potentially be available in the future through `conda forge`.
However, also direct installation is possible. A `pip` package is however not provided for that reason.
Testing is done using the conda version of GDAL with `pytest`.

There is also a **docker image** available at the [docker hub](https://hub.docker.com/r/tramsauer/raddo/) and [GitHub Container Registry](https://github.com/RaT0M/raddo/pkgs/container/raddo) if you don't mind the overhead. See the [Docker](#Docker) section below for instructions.

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

Download RADOLAN data from 14 days ago till *yesterday* to current directory with `raddo`.

For further arguments consult the help with `raddo --help`.

### CLI Example <a name="CLIExample"></a>

Download data since June 15th 2020 to current directory and sort, extract, create Geotiffs and a NetCDF file:
``` sh
raddo -s "2020-07-15" -C
```

Download `RADOLAN` data to *folder1* (`-d`) from *2020-07-15* (`-s`) until yesterday (default) for point in shapefile `test_pt.shp` (`-m`). Sort and extract nested archives and create GeoTiffs and a single NetCDF file from there (`-C`). Don't check for available files but just download all needed files (`-D`):
``` sh
raddo -d "folder1" -s "2020-07-15" -CD -m "test_pt.shp"
```

Download `RADOLAN` data to current folder for the last two weeks at point lat:48.4,lon:12.3, without asking for confirmation:
``` sh
raddo -p 12.3,48.4 -y
```


### Python Script <a name="PythonScript"></a>


``` python
import raddo as rd

rd.radolan_down(rad_dir_dwd = ...,  )
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

See [Changelog](CHANGELOG.rst) document.

## See also <a name="Seealso"></a>

- [wradlib](https://github.com/wradlib/wradlib):
  > An Open Source Library for Weather Radar Data Processing

- [radproc](https://github.com/jkreklow/radproc):
  > A GIS-compatible Python-Package for automated RADOLAN Composite Processing and Analysis
