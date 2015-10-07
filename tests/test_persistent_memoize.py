"""Tests the utils.persistent_memoize module of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import tempfile

from pyexperiment.utils.persistent_memoize import persistent_memoize
from pyexperiment.utils.persistent_memoize import PersistentCache
from pyexperiment import state


class TestPersistentMemoize(unittest.TestCase):
    """Tests the persistent_memoize decorator
    """
    def setUp(self):
        """Set up test fixture
        """
        pass

    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def test_cache_creates_state(self):
        """Test if the persistent cache creates an entry in the state
        """
        cache = PersistentCache('bla')
        self.assertIn(cache.KEY_PREFIX + 'bla', state)

    def test_cache_maps_to_state(self):
        """Test if the persistent cache maps correctly to an entry in the state
        """
        cache = PersistentCache('bla')
        cache[1] = 'foo'
        self.assertIn(cache.KEY_PREFIX + 'bla', state)
        self.assertIn(1, state[cache.KEY_PREFIX + 'bla'])
        self.assertEqual(state[cache.KEY_PREFIX + 'bla'][1], 'foo')

    def test_cache_uses_existing_state(self):
        """Test if the cache uses an existing entry in the state
        """
        state[PersistentCache.KEY_PREFIX + 'bla'] = {1: 12}
        cache = PersistentCache('bla')
        self.assertIn(1, cache)
        self.assertEqual(cache[1], 12)

    def test_cache_persists_reset(self):
        """Test if the cache persists after resetting and reloading state
        """
        cache = PersistentCache('bla')
        cache[1] = 42
        self.assertIn(1, cache)
        self.assertEqual(cache[1], 42)
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            state.load(temp.name)
            self.assertIn(1, cache)
            self.assertEqual(cache[1], 42)

    def test_memoizes(self):
        """Test if memoization works
        """
        called = [0]

        @persistent_memoize
        def target(arg):
            """Test function..."""
            called[0] += 1
            return 2 * arg

        result1 = target(1)
        self.assertEqual(result1, 2)
        self.assertEqual(called[0], 1)

        result2 = target(1)
        self.assertEqual(result2, 2)
        self.assertEqual(called[0], 1)

        result3 = target(2)
        self.assertEqual(result3, 4)
        self.assertEqual(called[0], 2)

        result4 = target(1)
        self.assertEqual(result4, 2)
        self.assertEqual(called[0], 2)

        result5 = target(2)
        self.assertEqual(result5, 4)
        self.assertEqual(called[0], 2)

    def test_memoizes_multiarg(self):
        """Test if memoization works with multiple arguments
        """
        called = [0]

        @persistent_memoize
        def target(arg1, arg2):
            """Test function..."""
            called[0] += 1
            return arg1 + arg2

        result1 = target(1, 2)
        self.assertEqual(result1, 3)
        self.assertEqual(called[0], 1)

        result2 = target(1, 2)
        self.assertEqual(result2, 3)
        self.assertEqual(called[0], 1)

    def test_memoizes_kwarg(self):
        """Test if memoization works with keyword arguments
        """
        called = [0]

        @persistent_memoize
        def target(arg1=0, arg2=1):
            """Test function..."""
            called[0] += 1
            return arg1 + arg2

        result1 = target()
        self.assertEqual(result1, 1)
        self.assertEqual(called[0], 1)

        result2 = target()
        self.assertEqual(result2, 1)
        self.assertEqual(called[0], 1)

        result3 = target(arg1=12)
        self.assertEqual(result3, 13)
        self.assertEqual(called[0], 2)

        result4 = target(arg1=12)
        self.assertEqual(result4, 13)
        self.assertEqual(called[0], 2)

        result5 = target(arg1=12, arg2=3)
        self.assertEqual(result5, 15)
        self.assertEqual(called[0], 3)

        result6 = target(arg1=12, arg2=3)
        self.assertEqual(result6, 15)
        self.assertEqual(called[0], 3)

    def test_memoizes_two_functions(self):
        """Test if memoization works with several functions
        """
        called = [0, 0]

        @persistent_memoize
        def target1(arg):
            """Test function..."""
            called[0] += 1
            return 2 * arg

        @persistent_memoize
        def target2(arg):
            """Test function..."""
            called[1] += 1
            return 3 * arg

        result1 = target1(1)
        self.assertEqual(result1, 2)
        self.assertEqual(called[0], 1)
        self.assertEqual(called[1], 0)

        result2 = target1(1)
        self.assertEqual(result2, 2)
        self.assertEqual(called[0], 1)
        self.assertEqual(called[1], 0)

        result3 = target2(1)
        self.assertEqual(result3, 3)
        self.assertEqual(called[0], 1)
        self.assertEqual(called[1], 1)

        result4 = target2(1)
        self.assertEqual(result4, 3)
        self.assertEqual(called[0], 1)
        self.assertEqual(called[1], 1)

    def test_persists(self):
        """Test if memoization persists
        """
        called = [0]

        def environment(expected_calls=1):
            """Creates target function in scope, check number of calls
            """
            @persistent_memoize
            def target(arg):
                """Test function..."""
                called[0] += 1
                return 2 * arg

            result1 = target(1)
            self.assertEqual(result1, 2)
            self.assertEqual(called[0], expected_calls)

            result2 = target(1)
            self.assertEqual(result2, 2)
            self.assertEqual(called[0], expected_calls)

        environment(expected_calls=1)
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            environment(expected_calls=2)
            environment(expected_calls=2)
            state.reset_instance()
            state.load(temp.name, lazy=True)
            environment(expected_calls=2)

    def test_triggers_state_changed(self):
        """Test if memoization triggers state change
        """
        with tempfile.NamedTemporaryFile() as temp:
            cache = PersistentCache('bla')
            state.save(temp.name)
            state.reset_instance()
            state.load(temp.name, lazy=True)
            self.assertFalse(state.changed)
            cache[1] = 42
            self.assertTrue(state.changed)


if __name__ == '__main__':
    unittest.main()
