"""Provides a way to memoize pure functions with the cache stored to the state.

For usage examples, check memoize in the examples folder.

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from toolz import memoize
from inspect import getsource

from pyexperiment import state


class PersistentCache(object):  # pylint: disable=too-few-public-methods
    """Persistent cache object that redirects to the state
    """
    KEY_PREFIX = '__persistent_cache_'
    """Prefix for the keys of the persistent cache in the state
    """

    def __init__(self, key):
        """Initializer
        """
        self.key = self.KEY_PREFIX + str(key)
        if self.key not in state:
            state[self.key] = {}

    def __getitem__(self, key):
        """Get cache entry
        """
        return state[self.key][key]

    def __setitem__(self, key, value):
        """Set cache entry
        """
        state[self.key][key] = value
        state.changed.add(self.key)

    def __iter__(self):
        """Iterator over the cache
        """
        return state[self.key].__iter__()


def persistent_memoize(target):
    """Memoize target function, keep persistent cache in state
    """
    target_hash = hash(getsource(target))
    cache = PersistentCache(target_hash)

    return memoize(target, cache=cache)
