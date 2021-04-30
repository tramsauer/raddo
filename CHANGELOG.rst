Changelog
=========

All notable changes to this project will be documented in this file.

`Unreleased changes <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.6.0...dev>`__

Version `0.?.? <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.5.1...0.5.?>`__ - 2020-11-??
----------------------------------------------------------------------------------------------
Changed
^^^^^^^

Added
^^^^^


Removed
^^^^^^^

Version `0.6.0 </compare/0.5.1...0.6.0>`__ - 2021-04-30
----------------------------------------------------------------------------------------------
Changed
^^^^^^^

-  fix sorting of flags and rename variables for clarity;
-  default start date now 14 days in the past
-  add flag to customize output NetCDF file name
  -  modify default name
  -  adjust missing dates attribute
-  add missing dates attribute to NetCDF file; code clean up
-  fix path issues if relative path is given (-d)
   - fix sorting base path
-  fix flow of interaction for netcdf creation and geotiff creation
-  clean exit if dir is not created
-  doc & README update


Added
^^^^^
- Dockerfile: raddo now available as docker image: `docker pull tramsauer/raddo`
- Travis integration

Removed
^^^^^^^
- Crontab section from README -> not relevant.


Version `0.5.1 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.5.0...0.5.1>`__ - 2020-09-25
----------------------------------------------------------------------------------------------
Changed
^^^^^^^

-  fix time issues
-  fix processing if folder available but empty
-  fix stdout
-  adjust stdout, use sys.stdout instead of print func
-  fix rad dir path issue.
-  fix data format issue - now correct values in netcdf!
-  change print to sys stdout function
-  change return filelist of available data in radolan_down
-  check folder (rad_dir) existance and create if missing

Added
^^^^^
-  add filling of missing dates in netCDF file creation
-  add time correction option, add timestamps on class level

Removed
^^^^^^^



Version `0.5.0 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.4.1...0.5.0>`__ - 2020-09-18
----------------------------------------------------------------------------------------------
Changed
^^^^^^^

-  fix data format issue - now correct values in netcdf!
-  change: return filelist of available data in radolan_down
-  check folder (rad_dir) existance and create if missing

Added
^^^^^
-  add time adjustment in netcdf

Removed
^^^^^^^



Version `0.4.1 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.4.0...0.4.1>`__ - 2020-07-22
----------------------------------------------------------------------------------------------
Changed
^^^^^^^

-  README update

Added
^^^^^

Removed
^^^^^^^


Version `0.4.0 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.3.2...0.4.0>`__ - 2020-07-22
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  changed from using ``xarray``/``rasterio`` to ``netCDF4`` package to
   fix memory leak

Added
^^^^^

Removed
^^^^^^^


Version `0.3.2 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.3.1...0.3.2>`__ - 2020-07-20
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  fixed installation requirements in ``setup.cfg``

Added
^^^^^

Removed
^^^^^^^


Version `0.3.1 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.3.0...0.3.1>`__ - 2020-07-17
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  update README to reflect changes

Added
^^^^^
Removed
^^^^^^^

Version `0.3.0 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.2.1...0.3.0>`__ - 2020-07-17
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  allow one day time spans
-  adjustments to lower memory usage
-  adjust stdout

Added
^^^^^

-  masking with shapefiles

Removed
^^^^^^^


Version `0.2.1 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.2.0...0.2.1>`__ - 2020-07-15
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  use a temporary directory if GeoTiffs not wanted

Added
^^^^^

-  add ``yes``-flag, to omit user feedback on actions
-  check count of to be created GeoTiffs

Removed
^^^^^^^


Version `0.2.0 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.1.1...0.2.0>`__ - 2020-07-15
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  change ``raddo`` to class object
-  cli default values changed

Added
^^^^^

-  tests

Removed
^^^^^^^


Version `0.1.1 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/0.1.0...0.1.1>`__ - 2020-07-01
----------------------------------------------------------------------------------------------

Changed
^^^^^^^

-  naming of default variables
-  pep-8

Added
^^^^^

Removed
^^^^^^^


Version `0.1.0 <https://gitlab.lrz.de/tramsauer/raddo/-/compare/ef2fa4...0.1.0>`__ - 2020-07-10
-----------------------------------------------------------------------------------------------

-  Initial release version.



--------------

*The format is based on*\ `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`__\ *and this project adheres to*\ `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__\ *.*
