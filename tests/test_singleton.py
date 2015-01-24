"""Tests the singleton class of pyexperiment

Written by Peter Duerr
"""

import unittest
from pyexperiment.utils.Singleton import Singleton


class TestSingleton(unittest.TestCase):
    """Test the Singleton class/mixin
    """
    def test_singleton_subclass(self):
        """Test that subclasses of Singleton always return same instance
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """

        a = SingletonTest.get_instance()
        b = SingletonTest.get_instance()
        self.assertEqual(a, b)
