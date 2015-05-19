"""Some functional tools for pyexperiment.

The `shorter` function compares the length of two iterators (one of
which may be of infinite length). The `starts_with` is similar to the
String's `startswith` function, but for iterators. The `flatten`
function will remove one level of nesting from a nested iterator.

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pyexperiment.utils import sentinel

if True:  # Ugly, but makes pylint happy
    # pylint:disable=import-error
    from six.moves import zip_longest


NONE = sentinel.create('NONE', 'Nothing')
"""Sentinel value for the functional
"""


def shorter(iter1, iter2):
    """Returns True if iterator 1 is shorter than iterator 2
    """
    for item1, item2 in zip_longest(iter1, iter2, fillvalue=NONE):
        if item2 is not NONE:
            if item1 is NONE:
                return True
        else:
            return False


def starts_with(iter1, iter2):
    """True if the first iterator starts with the elements of the second
    """
    equal_so_far = True
    for item1, item2 in zip_longest(iter1, iter2, fillvalue=NONE):
        if item2 is not NONE:
            if item1 is not NONE:
                equal_so_far = equal_so_far and item1 == item2
            else:
                return equal_so_far
        else:
            return False


def flatten(seq):
    """Flatten nested sequence
    """
    return (item for sublist in seq for item in sublist)
