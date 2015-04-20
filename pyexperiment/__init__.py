"""The pyexperiment module - quick and clean experiments with Python.
"""

from utils.Singleton import SingletonIndirector
from Config import Config

conf = SingletonIndirector(Config)
