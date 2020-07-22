=====
raddo
=====

|license badge|

This is the documentation of **raddo**.
*raddo* is a no-frills software that prepares RADOLAN weather radar
precipitation data for simple usage.

*raddo* downloads and processes RADOLAN weather radar ASCII data.
Downloaded files are sorted in folders based on year and month and may
also be decompressed. As next step *raddo* creates GeoTiffs in generic
WGS84 lat/lon coordinates and/or a single NetCDF file upon user request.
In case the data is only needed for a smaller region, masking via a
shapefile is also possible. For all possibilities on data retrieval and
processing see the *usage section*.

*raddo* tries to download all recent RADOLAN ASCII files / archives from
the DWD FTP server to the specified directory if files do not exist
already. A list of dates possibly available (default <current
year>-01-01 until today) is used to compare hypothetical available data
sets with actual local available ones. So file listing on the FTP side
is skipped due to (formerly) unreliable connection.

RADOLAN data from the German Weather Service (Deutscher Wetterdienst,
DWD) is copyrighted! Please find the copyright text
`here <https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf>`__.
The freely accessible data may be re-used without any restrictions
provided that the source reference is indicated, as laid down in the
GeoNutzV ordinance.

The RADOLAN precipitation data files are *updated daily* by DWD.

The data can be found at
`opendata.dwd.de <https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/radolan/recent/asc/>`__.


Contents
========

.. toctree::
   :maxdepth: 2

   Installation <install>
   Usage <usage>
   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Further Development
--------------------

- [X] add historical
- [X] integrate GeoTiff generation (reprojection)
- [X] integrate aggregation to NetCDF files
- [X] add tests!
- [ ] add docs
- [ ] add DOI
- [ ] pip install?
- [ ] add pypi install
- [ ] add conda install
- [X] gif for cli


See also
--------

-  `wradlib <https://github.com/wradlib/wradlib>`__: > An Open Source
   Library for Weather Radar Data Processing

-  `radproc <https://github.com/jkreklow/radproc>`__: > A GIS-compatible
   Python-Package for automated RADOLAN Composite Processing and
   Analysis


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. |license badge| image:: https://img.shields.io/badge/license-GNU_GPLv3-blue
   :target: :ref:`license`
