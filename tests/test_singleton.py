"""Tests the singleton class of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import


import unittest
from itertools import count as count_up

from pyexperiment.utils.Singleton import Singleton
from pyexperiment.utils.Singleton import InitializeableSingleton
from pyexperiment.utils.Singleton import delegate_singleton
from pyexperiment.utils.HierarchicalMapping import HierarchicalOrderedDict


class TestSingleton(unittest.TestCase):
    """Test the Singleton class/mixin
    """
    def test_singleton_subclass(self):
        """Test that subclasses of Singleton always return same instance
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """
            pass

        singleton_a = SingletonTest.get_instance()
        singleton_b = SingletonTest.get_instance()
        self.assertEqual(singleton_a, singleton_b)

    def test_singleton_resets(self):
        """Test that singletons properly reset themselves.
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                """Initializer
                """
                self.memory = []

            def add(self, number):
                """Append a number to the memory
                """
                self.memory.append(number)

        singleton_a = SingletonTest.get_instance()
        singleton_a.add(12)
        self.assertEqual(singleton_a.memory, [12])

        SingletonTest.reset_instance()

        singleton_b = SingletonTest.get_instance()
        self.assertNotEqual(singleton_a, singleton_b)

        self.assertEqual(singleton_b.memory, [])


class TestDelegatedSingleton(unittest.TestCase):
    """Test delegating singletons
    """
    def test_delegated_singleton_calls(self):
        """Test if the delegated singleton calls the singleton correctly
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                self.memory = []

            def add(self, number):
                """Add a number to the memory
                """
                self.memory.append(number)

            def reset(self):
                """Reset the memory
                """
                memory = self.memory
                self.memory = []
                return memory

        delegated = delegate_singleton(SingletonTest)
        delegated.add(12)

        self.assertEqual(delegated.memory, [12])

        memory = delegated.reset()
        self.assertEqual(memory, [12])
        self.assertEqual(delegated.memory, [])

    def test_delegated_get_instance(self):
        """Test if the delegated singleton can use get_instance
        """

        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                """Initializer
                """
                self.foo_str = "foo"

            def get_foo(self):
                """Returns the foo string
                """
                return self.foo_str

        delegated = delegate_singleton(SingletonTest)
        direct = delegated.get_instance()

        self.assertEqual(direct.get_foo(), "foo")

    def test_delegated_reset_instance(self):
        """Test if the delegated singleton can use reset_instance
        """
        class SingletonTest(Singleton):
            """Singleton test class
            """
            def __init__(self):
                """Initializer
                """
                self.memory = []

            def add(self, number):
                """Add a number to the memory
                """
                self.memory.append(number)

        delegated = delegate_singleton(SingletonTest)
        delegated.add(12)

        self.assertEqual(SingletonTest.get_instance().memory, [12])

        delegated.reset_instance()
        self.assertEqual(SingletonTest.get_instance().memory, [])

    def test_delegate_singleton_repr(self):
        """Test calling the repr method on a delegated singleton
        """
        class FooSingleton(Singleton):
            """Singleton test class
            """
            def __repr__(self):
                """Returns foo
                """
                return "foo"

        singleton = delegate_singleton(FooSingleton)
        self.assertEqual(singleton.__repr__(), "foo")

    def test_delegate_singleton_dir(self):
        """Test calling the dir method on a delegated singleton
        """
        class FooSingleton(Singleton):
            """Singleton test class
            """
            @staticmethod
            def bla():
                """Returns foo
                """
                return "foo"

        singleton = delegate_singleton(FooSingleton)
        self.assertIn('bla', dir(singleton))

    def test_delegate_singleton_iter(self):
        """Test iterating over a delegated singleton
        """
        class FooSingleton(Singleton, list):
            """Iterable Singleton
            """
            pass

        singleton = delegate_singleton(FooSingleton)

        for i in range(10):
            singleton.append(i)

        for item, expected in zip(singleton, count_up()):
            self.assertEqual(item, expected)

    def test_deletate_singleton_next(self):
        """Test using a delegated singleton as an iterator
        """
        class FooSingleton(Singleton):
            """Singleton Iterator
            """
            def __init__(self):
                """Initializer
                """
                self.state = 0

            def __iter__(self):
                """Make FooSingleton an iterator...
                """
                return self

            def __next__(self):
                """Returns the next value
                """
                if self.state < 3:
                    self.state += 1
                    return self.state
                else:
                    raise StopIteration

            def next(self):
                """For python 2.x compatibility"""
                return self.__next__()

        singleton = delegate_singleton(FooSingleton)

        for item, expected in zip(singleton, count_up(1)):
            self.assertEqual(item, expected)

    def test_delegate_hierarchical(self):
        """Test using a singleton HierarchicalOrderedDict
        """
        # pylint: disable=too-many-ancestors
        class SingletonDict(HierarchicalOrderedDict, Singleton):
            """Singleton Iterator
            """
            pass

        singleton = delegate_singleton(SingletonDict)
        singleton['a'] = 12
        singleton['b.c'] = 13

        self.assertIn('a', singleton)
        self.assertIn('b.c', singleton)
        self.assertEqual(singleton['a'], 12)
        self.assertEqual(singleton['b.c'], 13)

    def test_delegate_initializable(self):
        """Test using delegating an initializable singleton
        """
        memory = []

        class InitSingleton(InitializeableSingleton):
            """Initializable Singleton
            """
            def __init__(self):
                """Initializer
                """
                self.memory = []

            def append(self, value):
                """Append to the memory
                """
                self.memory.append(value)

            @classmethod
            def _get_pseudo_instance(cls):
                """Return the external memory
                """
                return memory

        singleton = delegate_singleton(InitSingleton)
        singleton.append(12)
        singleton.append(13)

        self.assertEqual(memory, [12, 13])
        singleton.initialize()

        singleton.append(14)
        singleton.append(15)
        self.assertEqual(memory, [12, 13])
        self.assertEqual(singleton.memory, [14, 15])
