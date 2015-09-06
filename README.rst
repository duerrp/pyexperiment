pyexperiment
============

|Version| |Python Version| |Build Status| |Coverage Status|

Pyexperiment facilitates the development of small, reproducible
experiments with minimal boilerplate code. Consider the following
example, implementing a simple program that stores numbers and
computes their sum:

.. code-block:: python

   from pyexperiment import experiment, state, conf, log

   conf['pyexperiment.save_state'] = True
   conf['pyexperiment.load_state'] = True
   conf['message'] = "The stored numbers are: "

   def store(number):
       """Store a number"""
       if 'numbers' not in state:
           log.debug("Initialize state['numbers'] to empty list")
           state['numbers'] = []

       log.debug("Store number: %s", number)
       state['numbers'].append(float(number))

    def show():
        """Show the stored numbers and compute their sum"""
        if not 'numbers' in state:
            print('No numbers stored yet')
            return

        print(conf['message'] + str(state['numbers']))
        with log.timed("sum"):
                total = sum(state['numbers'])
        print("The total is: " + str(total))

   if __name__ == '__main__':
       experiment.main(default=show,
                       commands=[store, show])


Pyexperiment makes it easy to experiment with this code from the
command line::

   $ ./numbers store 42
   $ ./numbers store 3.14
   $ ./numbers
   The stored numbers are: [42.0, 3.14]
   The total is: 45.14
   $ ./numbers -o message "Numbers: "
   Numbers: [42.0, 3.14]
   The total is: 45.14
   $ ./numbers -v
   [DEBUG   ] [0.069s] Start: './numbers -v'
   [DEBUG   ] [0.069s] Time: '2015-08-14 14:23:00.027378'
   [INFO    ] [0.075s] Loading state from file 'experiment_state.h5f'
   The stored numbers are: [42.0, 3.14]
   [DEBUG   ] [0.076s] sum took 0.000025s
   The total is: 45.14
   [DEBUG   ] [0.078s] No need to save unchanged state
   [DEBUG   ] [0.078s] End: './numbers -v show'
   [DEBUG   ] [0.078s] Time: '2015-08-14 14:23:00.037124'
   [DEBUG   ] [0.078s] Took: 0.010s
   $ ./numbers -h
   usage: numbers [-h] [-c CONFIG] [-o key value] [-i]
                  [--verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-v]
                  [-j PROCESSES]
                  [{store,show,help,test,show_tests,show_config,save_config,show_state,show_commands}]
                  [argument [argument ...]]

   Thanks for using numbers.

   positional arguments:
     {store,show,help,test,show_tests,show_config,save_config,show_state,show_commands}
                           choose a command to run, running show by default
     argument              argument to the command

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           specify a configuration file
     -o key value, --option key value
                           override a configuration option
     -i, --interactive     drop to interactive prompt after COMMAND
     --verbosity {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                           choose the console logger's verbosity
     -v                    shortcut for --verbosity DEBUG
     -j PROCESSES, --processes PROCESSES
                           set number of parallel processes used

   available commands:

     store:                Store a number
     show (default):       Show the stored numbers and compute their sum
     help:                 Shows help for a specified command
     test:                 Run tests for the experiment
     show_tests:           Show available tests for the experiment
     show_config:          Print the configuration
     save_config:          Save a configuration file to a filename
     show_state:           Shows the contents of the state loaded by the configuration or from the file specified as an argument
     show_commands:        Print the available commands


Motivation
----------

There is no shortage of great Python libraries for command line
interfaces, logging, configuration file management, persistent state,
parallelism, or plotting. When writing small scripts for quick
experiments though, it's often too much effort to configure these
components, and one ends up rewriting the same setup code over and
over again.

Pyexperiment fixes this by providing a simple way to jump start short
experiments. Importing pyexperiment will give you:

-  A basic *command line interface* that allows calling arbitrary
   functions (and passing arguments) from the command prompt,
   providing help text derived from the functions' docstrings and
   zsh/bash autocompletion (based on the standard library's argparse
   and argcomplete).
-  A simple *configuration management* with an easy way to provide
   default values (based on the excellent configobj library).
-  A thread-safe *logger* with configurable logging levels, *timing
   utilities* with statistics, and rotating log files (based on the
   standard library's logging module).
-  *Persistent state* with platform independent, configurable,
   (optionally rotating) state files that are compatible with many other
   programs (based on h5py).
-  *Parallel* execution of replicates.
-  A sensible setup for *plotting* (based on matplotlib, and optionally
   seaborn), with configurable defaults and asynchronous plotting.
-  Many other bits and pieces that might come in handy...

As a design principle, pyexperiment's components come ready to use
without any further configuration. Inevitably then, the choices made in
this setup are opinionated and may or may not fit your personal taste.
Feel free to start a discussion on the
`issues <https://github.com/duerrp/pyexperiment/issues>`__ page.

For more documentation, see the automatically generated pages `here
<https://pyexperiment.readthedocs.org>`__. For more usage examples,
check the `examples
<https://github.com/duerrp/pyexperiment/tree/master/examples>`__
folder.

Installation
------------

The easiest way to install pyexperiment is from pypi, just call ``pip install
--user pyexperiment`` (alternatively, use ``pip install pyexperiment`` in a
virtualenv, or prepend `sudo` for system wide installation).

The pyexperiment package has a few external dependencies (as you can
see in the `requirements.txt
<https://github.com/duerrp/pyexperiment/blob/master/docker/requirements.txt>`__):

-  six
-  configobj
-  numpy
-  h5py
-  matplotlib
-  lockfile
-  toolz
-  IPython (optional, allows using IPython with the --interactive command)
-  argcomplete (optional, adds activate_autocompletion command)
-  seaborn (optional, adds more plotting options)

If you install (the h5py dependency) from pypi, you may need to install
libhdf5 first, e.g., by running ``sudo apt-get install libhdf5-dev``.
You may also find that you need to install cython first, e.g., by
running either ``sudo apt-get install Cython`` or ``pip install
Cython``.

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
.. |Version| image:: https://img.shields.io/pypi/v/pyexperiment.svg
   :target: https://pypi.python.org/pypi/pyexperiment/
.. |Python Version| image:: https://img.shields.io/badge/python--version-2.7%203.2%203.3%203.4-blue.svg
   :target: https://pypi.python.org/pypi/pyexperiment/
.. |Build Status| image:: https://travis-ci.org/duerrp/pyexperiment.svg?branch=master
   :target: https://travis-ci.org/duerrp/pyexperiment
.. |Coverage Status| image:: https://coveralls.io/repos/duerrp/pyexperiment/badge.svg
   :target: https://coveralls.io/r/duerrp/pyexperiment
