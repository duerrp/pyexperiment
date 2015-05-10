"""The pyexperiment module - quick and clean experiments with Python.
"""
from pyexperiment.version import __version__

from pyexperiment.utils.Singleton import SingletonIndirector
from pyexperiment.utils.Singleton import InitializeableSingletonIndirector

# For convenience, set up the basic tools here
# pylint: disable=invalid-name
from pyexperiment.Config import Config
conf = InitializeableSingletonIndirector(Config)

from pyexperiment.Logger import TimingLogger
log = InitializeableSingletonIndirector(TimingLogger)

from pyexperiment.State import State
state = SingletonIndirector(State)
