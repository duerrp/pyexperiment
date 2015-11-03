"""Tests the config_conversion utilities of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest

from pyexperiment.utils.HierarchicalMapping import HierarchicalOrderedDict
from pyexperiment.utils.config_conversion import ohm_to_spec


class TestOhmToSpec(unittest.TestCase):
    """Test the ohm_to_spec function
    """
    def assert_equal_encoded_list(self, value, expected):
        """Assert the value list is equal to the encoded expected list
        """
        expected_enc = [item.encode() for item in expected]
        self.assertEqual(value, expected_enc)

    def test_empty_ohm(self):
        """Test converting empty ohm
        """
        ohm = HierarchicalOrderedDict()
        conf = ohm_to_spec(ohm)
        self.assertIsInstance(conf, list)

    def test_int_spec(self):
        """Test generating a spec from an integer
        """
        default = HierarchicalOrderedDict()
        default['a'] = 12
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["a = integer(default=12)"])

    def test_boolean_spec(self):
        """Test generating a spec from a boolean
        """
        default = HierarchicalOrderedDict()
        default['a'] = True
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["a = boolean(default=True)"])

    def test_string_spec(self):
        """Test generating a spec from a string
        """
        default = HierarchicalOrderedDict()
        default['a'] = "bla"
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["a = string(default=bla)"])

    def test_float_spec(self):
        """Test generating a spec from a float
        """
        default = HierarchicalOrderedDict()
        default['a'] = 1.2
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["a = float(default=1.2)"])

    def test_level1_spec(self):
        """Test generating a spec with one level
        """
        default = HierarchicalOrderedDict()
        default['a.b'] = 1.2
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["[a]", "b = float(default=1.2)"])

    def test_level1_spec_unordered(self):
        """Test generating a spec with one level and wrong order
        """
        default = HierarchicalOrderedDict()
        default['a.b'] = 1.2
        default['c'] = 3.4
        default['n.k'] = 2
        default['d.a'] = 3
        default['a.a'] = 1
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["c = float(default=3.4)",
             "[a]",
             "a = integer(default=1)",
             "b = float(default=1.2)",
             "[d]",
             "a = integer(default=3)",
             "[n]",
             "k = integer(default=2)"])

    def test_level2_spec(self):
        """Test generating a spec with two levels
        """
        default = HierarchicalOrderedDict()
        default['a.b'] = 1.2
        default['a.c.d'] = 3
        self.assert_equal_encoded_list(
            ohm_to_spec(default),
            ["[a]",
             "b = float(default=1.2)",
             "[[c]]",
             "d = integer(default=3)"])

if __name__ == '__main__':
    unittest.main()
