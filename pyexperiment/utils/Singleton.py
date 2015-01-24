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
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance
