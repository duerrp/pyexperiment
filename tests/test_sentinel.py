"""Tests the utils.sentinel module of pyexperiment

Note that some of the tests below are redundant, but they are kept here
as future python versions might change in an incompatible way (it
happened before...).

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
from copy import copy, deepcopy

from pyexperiment.utils import sentinel


class TestSentinel(unittest.TestCase):
    """Tests the sentinel
    """
    def setUp(self):
        """Set up test fixture
        """
        self.sentinel_a = sentinel.create('a')
        self.sentinel_b = sentinel.create('b', 'b_desc')
        self.sentinel_a2 = sentinel.create('a')
        self.sentinel_b2 = sentinel.create('b', 'b_desc')

    def test_sentinels_equal_self(self):
        """Test that the sentinel values are equal to themselves
        """
        self.assertEqual(self.sentinel_a, self.sentinel_a)
        self.assertEqual(self.sentinel_b, self.sentinel_b)

    def test_sentinel_is_self(self):
        """Test that sentinel is itself
        """
        self.assertIs(self.sentinel_a, self.sentinel_a)
        self.assertIs(self.sentinel_b, self.sentinel_b)

    def test_sentinel_id_equals_own_id(self):
        """Test that the id of a sentinel is pure
        """
        self.assertEqual(id(self.sentinel_a), id(self.sentinel_a))
        self.assertEqual(id(self.sentinel_b), id(self.sentinel_b))

    def test_sentinels_different(self):
        """Test that two different sentinels are always different
        """
        self.assertNotEqual(self.sentinel_a, self.sentinel_a2)
        self.assertNotEqual(self.sentinel_a, self.sentinel_b)
        self.assertNotEqual(self.sentinel_b, self.sentinel_b2)

    def test_sentinel_is_not_other(self):
        """Test that a sentinel is not another sentinel
        """
        self.assertIsNot(self.sentinel_a, self.sentinel_b)
        self.assertIsNot(self.sentinel_a, self.sentinel_a2)
        self.assertIsNot(self.sentinel_b, self.sentinel_b2)

    def test_sentinel_type_different(self):
        """Test that a sentinel never has the same type as another
        """
        self.assertNotEqual(type(self.sentinel_a), type(self.sentinel_b))
        self.assertNotEqual(type(self.sentinel_a), type(self.sentinel_a2))
        self.assertNotEqual(type(self.sentinel_b), type(self.sentinel_b2))

    def test_sentinel_id_different(self):
        """Test that a sentinel never has the same id as another
        """
        self.assertNotEqual(id(self.sentinel_a), id(self.sentinel_b))
        self.assertNotEqual(id(self.sentinel_a), id(self.sentinel_a2))
        self.assertNotEqual(id(self.sentinel_b), id(self.sentinel_b2))

    def test_sentinel_copy_is_same(self):
        """Test that a copy of a sentinel is the same
        """
        a_copy = copy(self.sentinel_a)
        b_copy = copy(self.sentinel_b)
        self.assertEqual(a_copy, self.sentinel_a)
        self.assertEqual(b_copy, self.sentinel_b)

    def test_sentinel_deepcopy_is_same(self):
        """Test that a copy of a sentinel is the same
        """
        a_copy = deepcopy(self.sentinel_a)
        b_copy = deepcopy(self.sentinel_b)
        self.assertEqual(a_copy, self.sentinel_a)
        self.assertEqual(b_copy, self.sentinel_b)

    def test_sentinel_description(self):
        """Test the repr of the sentinel
        """
        sen = sentinel.create('A', 'description')
        self.assertEqual(repr(sen), 'description')
