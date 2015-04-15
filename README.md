# pyexperiment

[![Development Status](https://pypip.in/status/pyexperiment/badge.svg)](https://pypi.python.org/pypi/pyexperiment/) [![Version](https://pypip.in/version/pyexperiment/badge.svg)](https://pypi.python.org/pypi/pyexperiment/) [![Python Version](https://pypip.in/py_versions/pyexperiment/badge.svg)](https://pypi.python.org/pypi/pyexperiment/) [![Build Status](https://travis-ci.org/duerrp/pyexperiment.svg?branch=master)](https://travis-ci.org/duerrp/pyexperiment) [![Coverage Status](https://coveralls.io/repos/duerrp/pyexperiment/badge.svg)](https://coveralls.io/r/duerrp/pyexperiment)

There is no shortage of great Python libraries for command line
interfaces, logging, configuration file management, persistent state,
or plotting. When writing small scripts for quick experiments though,
it's often too much effort to configure these components, and one ends
up rewriting the same setup code over and over again.

Pyexperiment fixes this by providing a very simple way to jump start a
short experiment, adding many features of a full-blown framework.

Importing one or several modules from pyexperiment will give you:

* A basic *command line interface* that allows calling arbitrary
  functions (and passing arguments) from the command prompt, providing
  help text derived from the functions' docstrings (based on the
  standard library's argparse).
* A simple *configuration management* with an easy way to provide
  default values (based on the excellent configobj library).
* A thread-safe *logger* with configurable logging levels, *timing
  utilities* with statistics, and rotating log files (based on the
  standard library's logging module).
* *Persistent state* with platform independent, configurable,
  (optionally rotating) state files that are compatible with many
  other programs (based on h5py).
* A sensible setup for *plotting* with configurable defaults (based on
  matplotlib).
* Many other bits and pieces that might come in handy...

As a design principle, pyexperiment's components come ready to use
without any further configuration. Inevitably then, the choices made
in this setup are opinionated and may or may not fit your personal
taste. Feel free to start a discussion on the [issues](https://github.com/duerrp/pyexperiment/issues) page.

For usage examples, check the [examples](https://github.com/duerrp/pyexperiment/tree/master/examples) folder.

## Dependencies

The pyexperiment package has a few external dependencies (as you can
see in the [requirements.txt](https://github.com/duerrp/pyexperiment/blob/master/requirements.txt)):

* configobj
* numpy
* h5py
* matplotlib

If you install the dependencies from pypi, you may need to install
libhdf5 first, e.g., by running `sudo apt-get install libhdf5-dev`.

## Reproducible experiments

To keep your experiments reproducible and avoid dependency problems,
it is a good idea to automate the setup of your development
environment, e.g., using a Vagrant box, or - in many cases even
better - a Docker image. To get started with pyexperiment using
Vagrant or Docker, you can use the Vagrantfile and setup script
[here](https://github.com/duerrp/pyexperiment/blob/master/vagrant), or
the Dockerfile and setup scripts
[here](https://github.com/duerrp/pyexperiment/blob/master/docker).

## License

The pyexperiment package is licensed under an MIT licence (see the
[LICENSE](https://github.com/duerrp/pyexperiment/blob/master/LICENSE)).
