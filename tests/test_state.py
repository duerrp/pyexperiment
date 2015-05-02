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
        self.list_val = [1, 2, 'a', 1.2]
        self.dict_val = {'a': 1, 1: 2.3}
        self.int_val = 123

    def tearDown(self):
        """Teardown test fixure
        """
        state.reset_instance()

    def set_up_basic_state(self):
        """Setup test fixure
        """
        state['list'] = self.list_val
        state['dict'] = self.dict_val
        state['values.int'] = self.int_val

    def test_set_get_first_level(self):
        """Test setting, getting state at the lowest level
        """
        state['a'] = 123
        self.assertEqual(state['a'], 123)

    def test_set_get_higher_levels(self):
        """Test setting, getting state at the higher levels
        """
        state['a.b'] = 123
        state['c.d.e'] = 345

        self.assertEqual(state['a.b'], 123)
        self.assertEqual(state['c.d.e'], 345)

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

    def test_save_rollover(self):
        """Test saving file with rollover
        """
        self.set_up_basic_state()
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name, rotate_n_state_files=2)

            # Write bogus info to state
            state['list'] = 'foo'
            state['dict'] = 'bar'
            state['values.int'] = 43

            state.save(temp.name, rotate_n_state_files=2)

            # Write more bogus info to state
            state['list'] = 'foo2'
            state['dict'] = 'bar2'
            state['values.int'] = 44

            state.save(temp.name, rotate_n_state_files=2)

            # Load original file
            state.load(temp.name + ".2", lazy=True)

            # Get loaded data
            list_val = state['list']
            dict_val = state['dict']
            int_val = state['values.int']

            self.assertEqual(self.list_val, list_val)
            self.assertEqual(self.dict_val, dict_val)
            self.assertEqual(self.int_val, int_val)

            # Load second file
            state.load(temp.name + ".1", lazy=True)

            # Get loaded data
            list_val = state['list']
            dict_val = state['dict']
            int_val = state['values.int']

            self.assertEqual('foo', list_val)
            self.assertEqual('bar', dict_val)
            self.assertEqual(43, int_val)

            # Load third file
            state.load(temp.name, lazy=True)

            # Get loaded data
            list_val = state['list']
            dict_val = state['dict']
            int_val = state['values.int']

            self.assertEqual('foo2', list_val)
            self.assertEqual('bar2', dict_val)
            self.assertEqual(44, int_val)

            # Remove temp files
            os.remove(temp.name + ".1")
            os.remove(temp.name + ".2")

    def test_need_saving(self):
        """Test the state.need_saving method
        """
        self.set_up_basic_state()
        self.assertTrue(state.need_saving())

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)

        self.assertFalse(state.need_saving())
        state['list'] = 'foo2'
        self.assertTrue(state.need_saving())

    def test_no_unnecessary_save(self):
        """Test saving the state only saves when necessary
        """
        self.assertFalse(state.need_saving())

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            self.assertEqual(os.stat(temp.name).st_size, 0)

        self.assertFalse(state.need_saving())

        state['bla'] = 'bla'
        self.assertTrue(state.need_saving())

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            self.assertNotEqual(os.stat(temp.name).st_size, 0)

        self.assertFalse(state.need_saving())

if __name__ == '__main__':
    unittest.main()
