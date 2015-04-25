"""The pyexperiment module - quick and clean experiments with Python.
"""
__version__ = '0.2.0'

from pyexperiment.utils.Singleton import SingletonIndirector
from pyexperiment.utils.Singleton import InitializeableSingletonIndirector

# For convenience, set up the basic tools here
# pylint: disable=invalid-name
from pyexperiment.Config import Config
conf = SingletonIndirector(Config)

from pyexperiment.Logger import TimingLogger
log = InitializeableSingletonIndirector(TimingLogger)

from pyexperiment.State import State
state = SingletonIndirector(State)
