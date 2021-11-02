.. _installation:

==============
Installation
==============

``raddo`` can be installed directly from source or be used from within a docker container.

.. note::

   The software is developed and tested for usage in Linux.
   Installation via pypi and conda are unfortunately not supported yet.


Install from source
++++++++++++++++++++

Installing ``raddo`` is simple: clone the repository, change into new directory and install via:

.. code:: bash

	  git clone <repo-url>
	  cd raddo
	  python setup.py install

or

.. code:: bash

    python setup.py develop

if you want to work on the code.

All requirements should be installed with raddo. But..


``GDAL`` is a requirement of ``raddo``.
Installation of this dependency can be a problem. If errors arise, ``GDAL`` binaries might be missing. When using *conda*, ``conda install -c conda-forge gdal`` might work. On Ubuntu (and derivates) using the ``UbuntuGIS-PPA`` seems to be working quite well.

Use docker instead
++++++++++++++++++++

Docker lets you run raddo in a containerized form.
All depenencies are set up - including GDAL.
`docker pull tramsauer/raddo` gets you the prebuilt image from docker-hub.
Alternatively, with the included `Dockerfile` the image can also be directly built with `docker build -t raddo .` from the root directory of the repository.
