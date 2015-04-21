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
    """Lock to prevent conflicts on the singleton instance
    """

    __singleton_instance = None
    """The singleton instance
    """

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


class InitializeableSingleton(Singleton):
    """Base-class for singleton that does not automatically initialize

    If get_instance is called on an uninitialized InitializeableSingleton,
    a pseudo-instance is returned.

    Sub-classes need to implement the function `_get_pseudo_instance`
    that returns a pseudo instance.
    """
    __singleton_lock = threading.Lock()
    """Lock to prevent conflicts on the singleton instance
    (redefined to get access)
    """
    __singleton_instance = None
    """The singleton instance (redefined to get access)
    """

    @classmethod
    def _get_pseudo_instance(cls):
        """Get pseudo instance before the real instance is initialized
        """
        raise NotImplementedError("Subclass should implement this.")

    @classmethod
    def get_instance(cls):
        """Get the singleton instance if its initialized.
        Returns, the pseudo instance if not.
        """
        if not cls.__singleton_instance:
            return cls._get_pseudo_instance()
        else:
            return cls.__singleton_instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance if its initialized.
        """
        if cls.__singleton_instance:
            with cls.__singleton_lock:
                if cls.__singleton_instance:
                    cls.__singleton_instance = None

    @classmethod
    def initialize(cls, *args, **kwargs):
        """Initializes the singleton.
        After calling this function, the real instance will be used.
        """
        cls.__singleton_instance = cls(*args, **kwargs)


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

    def __len__(self, *args):
        """Call __len__ on the singleton instance
        """
        return len(self.singleton.get_instance())


class InitializeableSingletonIndirector(SingletonIndirector):
    """Creates a class that mimics an InitializeableSingleton lazily
    """
    def initialize(self, *args, **kwargs):
        """Initializes the InitializeableSingleton
        """
        return self.singleton.initialize(*args, **kwargs)
