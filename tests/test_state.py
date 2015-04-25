"""Tests the state module of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import tempfile
import os

from pyexperiment import state


class TestState(unittest.TestCase):
    """Test pyexperiment's state
    """
    def setUp(self):
        """Setup test fixure
        """
        pass

    def tearDown(self):
        """Teardown test fixure
        """
        state.reset_instance()

    def set_up_basic_state(self):
        """Setup test fixure
        """
        self.list_val = [1, 2, 'a', 1.2]
        state['list'] = self.list_val
        self.dict_val = {'a': 1, 1: 2.3}
        state['dict'] = self.dict_val

        self.int_val = 123
        state['values.int'] = self.int_val

    def test_set_get_first_level(self):
        """Test setting, getting state at the lowest level
        """
        state['a'] = 123
        a = state['a']
        self.assertEqual(a, 123)

    def test_set_get_higher_levels(self):
        """Test setting, getting state at the higher levels
        """
        state['a.b'] = 123
        state['c.d.e'] = 345
        ab = state['a.b']
        self.assertEqual(ab, 123)
        abc = state['c.d.e']
        self.assertEqual(abc, 345)

    def test_get_inexistent(self):
        """Test getting non-existent value
        """
        self.assertRaises(KeyError, state.__getitem__, 'a')

    def test_save_load_file(self):
        """Test saving file and reloading yields identical values
        """
        self.set_up_basic_state()
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)

            # Write bogus info to state
            state['list'] = 'foo'
            state['dict'] = 'bar'
            state['values.int'] = 43

            state.load(temp.name, lazy=False)

            # Get loaded data
            list_val = state['list']
            dict_val = state['dict']
            int_val = state['values.int']

            self.assertEqual(self.list_val, list_val)
            self.assertEqual(self.dict_val, dict_val)
            self.assertEqual(self.int_val, int_val)

    def test_save_load_file_lazy(self):
        """Test saving file and reloading lazily yields identical values
        """
        self.set_up_basic_state()
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)

            # Write bogus info to state
            state['list'] = 'foo'
            state['dict'] = 'bar'
            state['values.int'] = 43

            state.load(temp.name, lazy=True)
            list_val = state['list']
            dict_val = state['dict']
            int_val = state['values.int']

            self.assertEqual(self.list_val, list_val)
            self.assertEqual(self.dict_val, dict_val)
            self.assertEqual(self.int_val, int_val)

if __name__ == '__main__':
    unittest.main()
