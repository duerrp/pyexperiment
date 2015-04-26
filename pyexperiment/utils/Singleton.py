"""Provides data structures for unique objects.

The `Singleton` class whose implementation is inspired by Tornado's
singleton (tornado.ioloop.IOLoop.instance()), can be inherited by
classes which only need to be instantiated once (for example a global
settings class such as :class:`pyexperiment.Config`). This design
pattern is often criticized, but it is hard to beat in terms of
simplicity.

A variant of the `Singleton`, the `InitializableSingleton` provides an
abstract base class for classes that are only instantiated once, but
need to provide an instance before being properly initialized (such as
`pyexperiment.Logger.Logger`).

The `SingletonIndirector` is a utility class that 'thunks' a
`Singleton` so that calls to the singleton instance's methods don't
need to be ugly chain calls. Similarly, the
`InitializeableSingletonIndirector` provides 'thunking' for the
`InitializeableSingleton`.

Written by Peter Duerr (Singleton inspired by Tornado's
implementation)

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
        if cls.__singleton_instance is None:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton
        """
        if cls.__singleton_instance is not None:
            with cls.__singleton_lock:
                if cls.__singleton_instance:
                    cls.__singleton_instance = None


class InitializeableSingleton(Singleton):
    """ABC for singleton that does not automatically initialize

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

    def __setitem__(self, *args):
        """Call __setitem__ on the singleton instance
        """
        return self.singleton.get_instance().__setitem__(*args)

    def __len__(self, *args):
        """Call __len__ on the singleton instance
        """
        return len(self.singleton.get_instance())

    def __contains__(self, *args):
        """Call __contains__ on the singleton instance
        """
        return self.singleton.get_instance().__contains__(*args)

    def __iter__(self, *args):
        """Call __iter__ on the singleton instance
        """
        return self.singleton.get_instance().__iter__(*args)

    def __next__(self, *args):
        """Call __next__ on the singleton instance
        """
        return self.singleton.get_instance().__next__(*args)


class InitializeableSingletonIndirector(SingletonIndirector):
    """Creates a class that mimics an InitializeableSingleton lazily
    """
    def initialize(self, *args, **kwargs):
        """Initializes the InitializeableSingleton
        """
        return self.singleton.initialize(*args, **kwargs)
