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

    def test_singleton_resets(self):
        """Test that singletons properly reset themselves.
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                self.memory = []

            def add(self, number):
                self.memory.append(number)

        a = SingletonTest.get_instance()
        a.add(12)
        self.assertEqual(a.memory, [12])

        SingletonTest.reset_instance()

        b = SingletonTest.get_instance()
        self.assertNotEqual(a, b)

        self.assertEqual(b.memory, [])
