"""A factory for unique sentinel values.

`Sentinel` objects are unique in the sense that they are equal only to
themselves. `Sentinel` objects can not be pickled.

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import inspect


def create(name, description=''):
    """Creates a new sentinel
    """
    if description == '':
        description = "Sentinel '%s'" % name

    class Sentinel(object):  # pylint: disable=too-few-public-methods
        """Sentinel class
        """
        def __init__(self):
            """Initializer
            """
            self.name = str(name)
            self.__name__ = self.name
            self.__class__.__name__ = self.name
            # Allow no instances
            self.__slots__ = ()

            # Make Sentinel belong to the module where it is created
            self.__class__.__module__ = inspect.stack(
                )[2][0].f_globals['__name__']

        def __repr__(self):
            """Represent the sentinel"""
            return description

        def __copy__(self):
            """Copy the sentinel returns itself
            """
            return self

        def __deepcopy__(self, _):
            """Copy the sentinel returns itself
            """
            return self

    # Create an instance, then make sure no one else can instantiate
    sentinel = Sentinel()

    del Sentinel
    return sentinel
