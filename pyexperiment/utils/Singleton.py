"""Provides data structures for unique objects.

The `Singleton` class whose implementation is inspired by Tornado's
singleton (tornado.ioloop.IOLoop.instance()), can be inherited by
classes which only need to be instantiated once (for example a global
settings class such as :class:`pyexperiment.Config`). This design
pattern is often criticized, but it is hard to beat in terms of
simplicity.

A variant of the `Singleton`, the `DefaultSingleton` provides an
abstract base class for classes that are only instantiated once, but
need to provide an instance before being properly initialized (such as
`pyexperiment.Logger.Logger`).

The function `delegate_singleton` 'thunks' a `Singleton` so that calls
to the singleton instance's methods don't need to be ugly chain calls.

Written by Peter Duerr (Singleton inspired by Tornado's
implementation)
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import threading
import inspect


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
                if cls.__singleton_instance is None:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton
        """
        if cls.__singleton_instance is not None:
            with cls.__singleton_lock:
                if cls.__singleton_instance is not None:
                    cls.__singleton_instance = None


class DefaultSingleton(Singleton):
    """ABC for singleton that does not automatically initialize

    If get_instance is called on an uninitialized DefaultSingleton,
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
        if cls.__singleton_instance is None:
            return cls._get_pseudo_instance()
        else:
            return cls.__singleton_instance

    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance if its initialized.
        """
        if cls.__singleton_instance is not None:
            with cls.__singleton_lock:
                if cls.__singleton_instance is not None:
                    cls.__singleton_instance = None

    @classmethod
    def initialize(cls, *args, **kwargs):
        """Initializes the singleton.
        After calling this function, the real instance will be used.
        """
        cls.__singleton_instance = cls(*args, **kwargs)


def delegate_special_methods(singleton):
    """Decorator that delegates special methods to a singleton
    """
    def _create_delegate(name, singleton):
        """Creates a thunk that calls the attribute on the singleton
        """
        def f(*args, **kwargs):
            """Calls the attribute on the singleton
            """
            ret = getattr(singleton.get_instance(),
                          name)(*args[1:], **kwargs)
            return ret
        return f

    def decorator(cls):
        """The decorator to be returned
        """
        for name, _attr in inspect.getmembers(singleton):
            if (name[:2], name[-2:]) != ('__', '__'):
                continue
            if name in ['__class__',
                        '__init__',
                        '__dict__',
                        '__new__',
                        '__doc__',
                        '__setattr__',
                        '__abstractmethods__',
                        '__delattr__',
                        '__getattribute__',
                        '__dir__']:
                continue
            setattr(cls, name, _create_delegate(name, singleton))
        return cls
    return decorator


def delegate_singleton(singleton):
    """Creates an object that delegates all calls to the singleton
    """
    # pylint: disable=too-few-public-methods
    @delegate_special_methods(singleton)
    class SingletonDelegate(object):
        """Passes attribute access to the singleton's instance
        """
        def __getattr__(self, attr):
            """Call __getattr__ on the singleton instance
            """
            return getattr(singleton.get_instance(), attr)

        @staticmethod
        def __dir__():
            """Pass __dir__
            """
            return dir(singleton.get_instance())

        @staticmethod
        def initialize(*args, **kwargs):
            """Pass initialize
            """
            singleton.initialize(*args, **kwargs)

    return SingletonDelegate()
