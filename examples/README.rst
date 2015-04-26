Getting Started
===============

The main idea behind pyexperiment is to make starting a short
experiment as simple as possible without sacrificing the comfort of
some basic facilities like a reasonable CLI, logging, persistent
state, configuration management, plotting and timing.

Motivating Example
------------------

Let's assume we need to write a quick and clean script that reads a
couple of files with time series data and computes the average value.
We also want to generate a plot of the data.

CLI
~~~

To be efficient, we split our script into three functions. `read`
should read one or multiple raw data files, `average` should compute
the average of the data in the read files and `plot` should plot the
data over time. Moreover, we want to add a test for the average
function to make sure it's working correctly. In pyexperiment, we can
achieve a CLI with these functions very easily. Let's write the basic
structure of our script to a file, say 'analyzer.py'

.. code-block:: python

   #!/usr/bin/env python
   from pyexperiment import experiment
   
   def read(*filenames):
       pass
   
   def average():
       pass
   
   def plot():
       pass
   
   class AverageTest(unittest.TestCase):
       """Tests the average function
       """
       pass
   
   if __name__ == 'main':
       experiment(commands=[load, average, plot],
                  tests=[AverageTest])
   

Without any further code, the call to `experiment` will set up a
command line interface for our application that allows executing the
three functions `read`, `average`, and `plot` by calling `analyzer
read ./datafile1 ./datafile2`, `analyzer average`, and `analyzer plot`
respectively. A call to `analyzer test` will run our (yet
unimplemented) unittests.

State
~~~~~

Next, let's write the `read` function and save the loaded data to a
persistent state file. To this end, we can use pyexperiment's `state`
which we get by adding `from pyexperiment import state` and `from
pyexperiment.experiment import save_state` to the top of
'analyzer.py'. Then, assuming the data files consist of comma
separated values, we can achieve this by defining `load` as

.. code-block:: python

   def read(*filenames):
       """Reads data files and stores their content
       """
       # Initialize the state with an empty list for the data
       state['data'] = []
       for filename in filenames:
           with open(filename) as f:
               state['data'] += [float(data)
                                 for data in f.readlines()]
       save_state()

Logging
~~~~~~~

In order to better understand our results, it would be nice to have a
logger to print some debug output, e.g., printing the names of the
files we load and how many data points they contain. A few calls to
pyexperiment's logger will do the job - simply add `from pyexperiment
import log` and add logging calls at the desired level:

.. code-block:: python

   def read(*filenames):
       """Reads data files and stores their content
       """
       # Initialize the state with an empty list for the data
       state['data'] = []
       for filename in filenames:
           log.info("Reading file %s", filename)
           with open(filename) as f:
               data = [float(data)
                       for data in f.readlines()]
               if len(data) == 0:
                   log.warning("Datafile %s does not contain any data",
                               filename)
               log.debug("Read %i datapoints", len(data))
               state['data'] += data
       save_state()

Configuration
~~~~~~~~~~~~~

You will notice that by default, pyexperiment does not log to a file
and it will only print messages at, or above the 'WARNING' level. If
you would like to see more (or less) messages, you can change the
logging level by runnint the analyzer with an additional argument
e.g., `-o verbosity DEBUG`. In general, any configuration option can
be set from the command line with `-o [level[.level2.[...]]].key
value`.

The `verbosity` configuration value is predefined by pyexperiment, but
we can use the same configuration mechanism for our own parameters.
This is achieved by defining a specification for the configuration and
passing it as the `config_spec` argument to the `experiment` call. For
example, we may want to add an option to ignore data files longer
than a certain length:

.. code-block:: python

   CONFIG_SPEC = ("[read]\n"
                  "max_length = integer(min=1, default=100)\n")

   if __name__ == '__main__':       
       experiment(commands=[load, average, plot],
                  tests=[AverageTest],
                  config_spec=CONFIG_SPEC)

We can then access the parameters by adding `from pyexperiment import
conf` at the top of 'analyzer.py' and calling `conf` like a dictionary
with the levels of the configuration separated by dots:

.. code-block:: python

   def read(*filenames):
       """Reads data files and stores their content
       """
       # Initialize the state with an empty list for the data
       state['data'] = []

       # Get the max length from the configuration
       max_length = conf['read.max_length']
       
       for filename in filenames:
           log.info("Reading file %s", filename)
           with open(filename) as f:
               data = [float(data)
                       for data in f.readlines()]
               if len(data < max_length):
                   if len(data) == 0:
                       log.warning("Datafile %s does not contain any data",
                                   filename)
                   log.debug("Read %i datapoints", len(data))
                   state['data'] += data
               else:
                   log.warning("Datafile %s too long. Ignoring data")
                   
       save_state()
                  
By default, pyexperiment will try to load a file called 'config.ini'
(if necessary, one can of course override this default filename). To
generate an initial configuration file with the default options,
simply run `analyzer save_config ./config.ini`. Any options set in the
resulting file will be used in future runs.

Timing
~~~~~~

If we are loading big data files, we may also be interested to learn
how much time it takes to load an individual file - there may be some
room for optimization. To measure the time it takes to load a file and
compute statistics, we can use pyexperiment's timing function (see the
docs for more information).

To be continued...
