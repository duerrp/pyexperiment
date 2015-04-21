"""Implements a singleton base-class (as in tornado.ioloop.IOLoop.instance())

Written by Peter Duerr (inspired by tornado's implementation)
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import threading


class Singleton(object):
    """Singleton base-class (or mixin)
    """
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance
        """
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton
        """
        if cls.__singleton_instance:
            with cls.__singleton_lock:
                if cls.__singleton_instance:
                    cls.__singleton_instance = None


class SingletonIndirector(object):
    """Creates a class that mimics the Singleton lazily

    This avoids calling obj.get_instance().attribute too often
    """
    def __init__(self, singleton):
        """Initializer
        """
        self.singleton = singleton

    def __getattr__(self, attr):
        """Call __getattr__ on the singleton instance
        """
        return getattr(self.singleton.get_instance(), attr)

    def __repr__(self):
        """Call __repr__ on the singleton instance
        """
        return repr(self.singleton.get_instance())

    def __dir__(self):
        """Get the methods of the underlying singleton
        """
        return dir(self.singleton.get_instance())

    def __getitem__(self, *args):
        """Call __getitem__ on the singleton instance
        """
        return self.singleton.get_instance().__getitem__(*args)
