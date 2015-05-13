"""Tests the utils.functional module of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from itertools import count
import unittest

if True:  # Ugly, but makes pylint happy
    # pylint:disable=import-error
    from six.moves import range  # pylint: disable=redefined-builtin


from pyexperiment.utils.functional import shorter, starts_with


class TestShorter(unittest.TestCase):
    """Test the shorter function
    """
    def test_shorter_lists(self):
        """Test shorter function on lists
        """
        self.assertTrue(shorter([], [1]))
        self.assertTrue(shorter([1, 2], [1, 2, 3]))

        self.assertFalse(shorter([1], []))
        self.assertFalse(shorter([1, 2, 3], [1, 2]))

    def test_shorter_generators(self):
        """Test shorter function on generators
        """
        self.assertTrue(shorter(range(10), range(20)))
        self.assertFalse(shorter(range(3), range(2)))

        self.assertTrue(shorter(range(20), count()))
        self.assertFalse(shorter(count(), range(20)))

    def test_shorter_gen_and_list(self):
        """Test shorter function on generators and lists
        """
        self.assertTrue(shorter(range(2), [1, 2, 3]))
        self.assertFalse(shorter([1, 2, 3, 4], range(2)))

        self.assertTrue(shorter([0], count()))
        self.assertFalse(shorter(count(), [1, 2, 3]))


class TestStartsWith(unittest.TestCase):
    """Test the starts_with function
    """
    def test_starts_with_lists(self):
        """Test starts_with function on lists
        """
        self.assertTrue(starts_with([1], [1, 2]))
        self.assertTrue(starts_with(['a', 'b'], ['a', 'b', 'c']))

        self.assertFalse(starts_with([1], []))
        self.assertFalse(starts_with([1, 2, 3], [3, 2, 1, 3]))

    def test_starts_with_generators(self):
        """Test starts_with function on generators
        """
        self.assertTrue(starts_with(range(10), range(20)))
        self.assertFalse(starts_with(range(1, 3), range(4)))

        self.assertTrue(starts_with(range(20), count()))
        self.assertFalse(starts_with(count(), range(20)))

    def test_starts_with_gen_and_list(self):
        """Test starts_with function on generators and lists
        """
        self.assertTrue(starts_with(range(2), [0, 1, 2, 3]))
        self.assertFalse(starts_with([1, 2, 3, 4], range(4)))

        self.assertTrue(starts_with([0], count()))
        self.assertFalse(starts_with(count(), [1, 2, 3]))
