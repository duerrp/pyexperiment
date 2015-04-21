"""Tests the singleton class of pyexperiment

Written by Peter Duerr
"""

import unittest
from pyexperiment.utils.Singleton import Singleton, SingletonIndirector


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

    def test_indirector_calls(self):
        """Test if the indirector calls the singleton correctly
        """

        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                self.memory = []

            def add(self, number):
                self.memory.append(number)

            def reset(self):
                memory = self.memory
                self.memory = []
                return memory

        indirect = SingletonIndirector(SingletonTest)
        indirect.add(12)

        self.assertEqual(indirect.memory, [12])

        memory = indirect.reset()
        self.assertEqual(memory, [12])
        self.assertEqual(indirect.memory, [])

    def test_indirector_get_instance(self):
        """Test if the indirector can use get_instance
        """

        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                pass

            def foo(self):
                return "foo"

        indirect = SingletonIndirector(SingletonTest)
        direct = indirect.get_instance()

        self.assertEqual(direct.foo(), "foo")

    def test_indirector_reset_instance(self):
        """Test if the indirector can use reset_instance
        """

        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                self.memory = []

            def add(self, number):
                self.memory.append(number)

        indirect = SingletonIndirector(SingletonTest)
        indirect.add(12)

        self.assertEqual(SingletonTest.get_instance().memory, [12])

        indirect.reset_instance()
        self.assertEqual(SingletonTest.get_instance().memory, [])
