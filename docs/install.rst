.. _installation:

==============
Installation
==============


.. note::

   The software is developed and tested for usage in Linux.
   Installation via pip and conda are unfortunately not supported yet.

Installing ``raddo`` is simple: clone the repository, change into new directory and run:

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
