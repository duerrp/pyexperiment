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
import io
import six

# For python2.x compatibility
from six.moves import range  # pylint: disable=redefined-builtin, import-error

from pyexperiment import state
from pyexperiment.utils.stdout_redirector import stdout_redirector


class StateTester(unittest.TestCase):
    """ABC for state's test fixures
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

    def _setup_basic_state(self):
        """Setup test fixure
        """
        state['list'] = self.list_val
        state['dict'] = self.dict_val
        state['values.int'] = self.int_val


class TestBasicState(StateTester):
    """Test basic functionality of pyexperiment's state
    """
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

    def test_show(self):
        """Test showing the state
        """
        state['a.b'] = 12
        state['bla.bli'] = 13

        buf = io.StringIO()
        with stdout_redirector(buf):
            state.show()

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r"\[a\]")
        self.assertRegexpMatches(buf.getvalue(), r"\[bla\]")
        self.assertRegexpMatches(buf.getvalue(), r"b")
        self.assertRegexpMatches(buf.getvalue(), r"bli")
        self.assertRegexpMatches(buf.getvalue(), r"12")
        self.assertRegexpMatches(buf.getvalue(), r"13")

    def test_in_lazy(self):
        """Test checking for an attribute in a lazily loaded state
        """
        self._setup_basic_state()
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('list', state)
            state.load(temp.name, lazy=True)
            self.assertIn('list', state)

    def test_delete_from_state(self):
        """Test deleting a value from the state
        """
        self._setup_basic_state()
        self.assertIn('list', state)
        del state['list']
        self.assertNotIn('list', state)

    def test_show_lazy(self):
        """Test showing the state lazily loaded
        """
        state['a.b'] = 12
        buf = io.StringIO()

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state['a.b'] = 13
            state.load(temp.name, lazy=True)

            with stdout_redirector(buf):
                state.show()
            self.assertNotEqual(len(buf.getvalue()), 0)
            self.assertRegexpMatches(buf.getvalue(), r"\[a\]")
            self.assertRegexpMatches(buf.getvalue(), r"b")
            self.assertRegexpMatches(buf.getvalue(), r"12")
            if six.PY2:
                self.assertNotRegexpMatches(buf.getvalue(), r"13")
            elif six.PY3:
                self.assertNotRegex(  # pylint: disable=E1101
                    buf.getvalue(), r"13")

    def test_show_nonexisting_noraise(self):
        """Test showing a state that does not exist
        """
        buf = io.StringIO()
        with stdout_redirector(buf):
            state.show()

        self.assertEqual(len(buf.getvalue()), 0)

    def test_load_nonexisting(self):
        """Test loading a state that does not exist with error flag default
        """
        temp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(temp.name)
        self.assertRaises(IOError, state.load, temp.name, lazy=False)

    def test_load_nonexisting_lazy(self):
        """Test loading a state that does not exist with error flag default
        """
        temp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(temp.name)
        self.assertRaises(IOError, state.load, temp.name, lazy=True)

    def test_load_nonexisting_noraise(self):
        """Test loading a state that does not exist with error flag True
        """
        temp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(temp.name)
        state.load(temp.name, lazy=False, raise_error=False)
        self.assertEqual(len(state), 0)

    def test_load_nonexist_lazy_noraise(self):
        """Test loading a state that does not exist with error flag default
        """
        temp = tempfile.NamedTemporaryFile(delete=False)
        os.remove(temp.name)
        state.load(temp.name, lazy=True, raise_error=False)

        self.assertNotIn('foo', state)

    def test_keys(self):
        """Test getting the keys in a state
        """
        self._setup_basic_state()
        self.assertEqual(len(state.keys()), 3)
        self.assertIn('list', state.keys())
        self.assertIn('dict', state.keys())
        self.assertIn('values.int', state.keys())


class TestStateIO(StateTester):
    """Test save/load functionality of pyexperiment's state
    """
    def test_save_load_file(self):
        """Test saving file and reloading yields identical values
        """
        self._setup_basic_state()
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
        self._setup_basic_state()
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
        # Write some stuff to the state
        state['a'] = (-1) ** 2
        state['b'] = (-1) ** 3
        state['c'] = 41

        with tempfile.NamedTemporaryFile() as temp:
            # Save original state
            state.save(temp.name, rotate_n_state_files=2)

            for i in range(10):
                # Write bogus info to state
                state['a'] = i**2
                state['b'] = i**3
                state['c'] = 42 + i

                state.save(temp.name, rotate_n_state_files=2)

                # Load last file and check contents
                state.load(temp.name + ".1", lazy=True)
                self.assertEqual(state['a'], (i - 1) ** 2)
                self.assertEqual(state['b'], (i - 1) ** 3)
                self.assertEqual(state['c'], 42 + (i - 1))

                if i > 0:
                    # Load previous to last file and check contents
                    state.load(temp.name + ".2", lazy=True)
                    self.assertEqual(state['a'], (i - 2) ** 2)
                    self.assertEqual(state['b'], (i - 2) ** 3)
                    self.assertEqual(state['c'], 42 + (i - 2))

                # Load current state and check contents
                state.load(temp.name, lazy=True)
                self.assertEqual(state['a'], i ** 2)
                self.assertEqual(state['b'], i ** 3)
                self.assertEqual(state['c'], 42 + i)

            # Remove temp files
            os.remove(temp.name + ".1")
            os.remove(temp.name + ".2")

    def test_need_saving(self):
        """Test the state.need_saving method
        """
        self._setup_basic_state()
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
