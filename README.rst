pyexperiment
============

|Development Status| |Version| |Python Version| |Build Status| |Coverage
Status|

There is no shortage of great Python libraries for command line
interfaces, logging, configuration file management, persistent state, or
plotting. When writing small scripts for quick experiments though, it's
often too much effort to configure these components, and one ends up
rewriting the same setup code over and over again.

Pyexperiment fixes this by providing a simple way to jump start a
short experiment. Importing pyexperiment will give you:

-  A basic *command line interface* that allows calling arbitrary
   functions (and passing arguments) from the command prompt, providing
   help text derived from the functions' docstrings (based on the
   standard library's argparse).
-  A simple *configuration management* with an easy way to provide
   default values (based on the excellent configobj library).
-  A thread-safe *logger* with configurable logging levels, *timing
   utilities* with statistics, and rotating log files (based on the
   standard library's logging module).
-  *Persistent state* with platform independent, configurable,
   (optionally rotating) state files that are compatible with many other
   programs (based on h5py).
-  A sensible setup for *plotting* with configurable defaults (based on
   matplotlib).
-  Many other bits and pieces that might come in handy...

As a design principle, pyexperiment's components come ready to use
without any further configuration. Inevitably then, the choices made in
this setup are opinionated and may or may not fit your personal taste.
Feel free to start a discussion on the
`issues <https://github.com/duerrp/pyexperiment/issues>`__ page.

For more documentation, see the automatically generated pages `here
<https://pyexperiment.readthedocs.org>`__. For usage examples, check
the `examples
<https://github.com/duerrp/pyexperiment/tree/master/examples>`__
folder.

Dependencies
------------

The pyexperiment package has a few external dependencies (as you can see
in the
`requirements.txt <https://github.com/duerrp/pyexperiment/blob/master/requirements.txt>`__):

-  six
-  configobj
-  numpy
-  h5py
-  matplotlib
-  IPython (optional)

If you install the dependencies from pypi, you may need to install
libhdf5 first, e.g., by running ``sudo apt-get install libhdf5-dev``.

Reproducible experiments
------------------------

To keep your experiments reproducible and avoid dependency problems, it
is a good idea to automate the setup of your development environment,
e.g., using a Vagrant box, or - in many cases even better - a Docker
image. To get started with pyexperiment using Vagrant or Docker, you can
use the Vagrantfile and setup script
`here <https://github.com/duerrp/pyexperiment/blob/master/vagrant>`__,
or the Dockerfile and setup scripts
`here <https://github.com/duerrp/pyexperiment/blob/master/docker>`__.

License
-------

The pyexperiment package is licensed under an MIT licence (see the
`LICENSE <https://github.com/duerrp/pyexperiment/blob/master/LICENSE>`__).

.. |Development Status| image:: https://pypip.in/status/pyexperiment/badge.svg
   :target: https://pypi.python.org/pypi/pyexperiment/
.. |Version| image:: https://pypip.in/version/pyexperiment/badge.svg
   :target: https://pypi.python.org/pypi/pyexperiment/
.. |Python Version| image:: https://pypip.in/py_versions/pyexperiment/badge.svg
   :target: https://pypi.python.org/pypi/pyexperiment/
.. |Build Status| image:: https://travis-ci.org/duerrp/pyexperiment.svg?branch=master
   :target: https://travis-ci.org/duerrp/pyexperiment
.. |Coverage Status| image:: https://coveralls.io/repos/duerrp/pyexperiment/badge.svg
   :target: https://coveralls.io/r/duerrp/pyexperiment
