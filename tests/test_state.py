"""Tests the state module of pyexperiment

Written by Peter Duerr
"""

import unittest
import tempfile
import os

from pyexperiment import state


class TestSetGetState(unittest.TestCase):
    """Test setting and getting state
    """
    def setUp(self):
        """Setup test fixure
        """
        pass

    def tearDown(self):
        """Teardown test fixure
        """
        state.reset_instance()

    def test_set_get_first_level(self):
        """Test setting, getting state at the lowest level
        """
        state.set_state('a', 123)
        a = state.get_state('a')
        self.assertEqual(a, 123)

    def test_set_get_higher_levels(self):
        """Test setting, getting state at the higher levels
        """
        state.set_state('a.b', 123)
        state.set_state('c.d.e', 345)
        ab = state.get_state('a.b')
        self.assertEqual(ab, 123)
        abc = state.get_state('c.d.e')
        self.assertEqual(abc, 345)

    def test_get_inexistent(self):
        """Test getting non-existent value
        """
        self.assertRaises(KeyError, state.get_state, 'a')


class TestSaveLoadState(unittest.TestCase):
    """Test saving and loading state
    """
    def setUp(self):
        """Setup test fixure
        """
        self.list_val = [1, 2, 'a', 1.2]
        state.set_state('list', self.list_val)

        self.dict_val = {'a': 1, 1: 2.3}
        state.set_state('dict', self.dict_val)

        self.int_val = 123
        state.set_state('values.int', self.int_val)

    def tearDown(self):
        """Teardown test fixure
        """
        state.reset_instance()

    def test_save_load_file(self):
        """Test saving file and reloading yields identical values
        """
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)

            # Write bogus info to state
            state.set_state('list', 'foo')
            state.set_state('dict', 'bar')
            state.set_state('values.int', 43)

            state.load(temp.name, lazy=False)

            # Get loaded data
            list_val = state.get_state('list')
            dict_val = state.get_state('dict')
            int_val = state.get_state('values.int')

            self.assertEqual(self.list_val, list_val)
            self.assertEqual(self.dict_val, dict_val)
            self.assertEqual(self.int_val, int_val)

    def test_save_load_file_lazy(self):
        """Test saving file and reloading lazily yields identical values
        """
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)

            # Write bogus info to state
            state.set_state('list', 'foo')
            state.set_state('dict', 'bar')
            state.set_state('values.int', 43)

            state.load(temp.name, lazy=True)

            # Get loaded data
            list_val = state.get_state('list')
            dict_val = state.get_state('dict')
            int_val = state.get_state('values.int')

            self.assertEqual(self.list_val, list_val)
            self.assertEqual(self.dict_val, dict_val)
            self.assertEqual(self.int_val, int_val)

if __name__ == '__main__':
    unittest.main()
