"""The pyexperiment module - quick and clean experiments with Python.
"""
from pyexperiment.version import __version__

from pyexperiment.utils.Singleton import delegate_singleton

# For convenience, set up the basic tools here
# pylint: disable=invalid-name
from pyexperiment.Config import Config
conf = delegate_singleton(Config)

from pyexperiment.Logger import TimingLogger
log = delegate_singleton(TimingLogger)

from pyexperiment.State import State
state = delegate_singleton(State)
