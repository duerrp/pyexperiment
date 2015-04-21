"""The pyexperiment module - quick and clean experiments with Python.
"""

from pyexperiment.utils.Singleton import SingletonIndirector
from pyexperiment.utils.Singleton import InitializeableSingletonIndirector
from pyexperiment.Config import Config
from pyexperiment.Logger import TimingLogger

# For convenience, set up the basic tools here
# pylint: disable=invalid-name
conf = SingletonIndirector(Config)
log = InitializeableSingletonIndirector(TimingLogger)
