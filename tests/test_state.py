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
import shutil
import multiprocessing
import numpy as np

# For python2.x compatibility
from six.moves import range  # pylint: disable=redefined-builtin, import-error

from pyexperiment import state
from pyexperiment.State import StateHandler
from pyexperiment.utils.stdout_redirector import stdout_redirector


class StateTester(unittest.TestCase):
    """ABC for state's test fixtures
    """
    def setUp(self):
        """Setup test fixture
        """
        self.list_val = [1, 2, 'a', 1.2]
        self.dict_val = {'a': 1, 1: 2.3}
        self.int_val = 123

    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def _setup_basic_state(self):
        """Setup test fixture
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

    def test_get_section(self):
        """Test getting a section of the state
        """
        state['a.a'] = 12
        state['a.b'] = 13
        state['c'] = 24

        self.assertIn('a', state)
        section_a = state['a']
        self.assertIn('a', section_a)
        self.assertIn('b', section_a)
        self.assertNotIn('c', section_a)
        self.assertEqual(section_a['a'], 12)
        self.assertEqual(section_a['b'], 13)

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

    def test_setting_increases_length(self):
        """Test setting items increases length
        """
        self.assertEqual(len(state), 0)
        state['a'] = 12
        self.assertEqual(len(state), 1)
        state['c.d.f'] = 13
        self.assertEqual(len(state), 2)

    def test_delete_from_state(self):
        """Test deleting a value from the state
        """
        state['list'] = [1, 2, 3]
        self.assertIn('list', state)
        del state['list']
        self.assertNotIn('list', state)

    def test_delete_reduces_length(self):
        """Test deleting a value from the state reduces the length
        """
        self._setup_basic_state()
        no_items = len(state)
        del state['list']
        self.assertEqual(len(state), no_items - 1)

    def test_delete_removes_key(self):
        """Test deleting a value from the state removes the item
        """
        self._setup_basic_state()
        del state['list']
        self.assertNotIn('list', state.keys())

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
            else:
                raise RuntimeError("Python version not supported")

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

    def test_empty_keys(self):
        """Test getting the keys in an empty state
        """
        self.assertEqual(len(state.keys()), 0)

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

    def test_load_wo_filenamee(self):
        """Test loading state without passing a filename
        """
        self.assertRaises(RuntimeError, state.load)

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

    def test_get_section_lazy(self):
        """Test getting a section of the state lazily
        """
        state['a.a'] = 12
        state['a.b'] = 13
        state['c'] = 24

        self.assertIn('a', state)
        section_a = state['a']
        self.assertIn('a', section_a)
        self.assertIn('b', section_a)
        self.assertNotIn('c', section_a)
        self.assertEqual(section_a['a'], 12)
        self.assertEqual(section_a['b'], 13)

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('a', state)

            state.load(temp.name)

            self.assertIn('a', state)

            section_a = state['a']

            self.assertIn('a', section_a)
            self.assertIn('b', section_a)
            self.assertNotIn('c', section_a)
            self.assertEqual(section_a['a'], 12)
            self.assertEqual(section_a['b'], 13)

    def test_get_section_lazy2(self):
        """Test getting directly a section of the state lazily
        """
        state['a.b'] = 12

        self.assertIn('a.b', state)
        self.assertEqual(state['a.b'], 12)

        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()

            state.load(temp.name)

            self.assertIn('a.b', state)
            self.assertEqual(state['a.b'], 12)

    def test_lazy_really_lazy(self):
        """Test lazy loading is really lazy
        """
        self._setup_basic_state()
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp2 = tempfile.NamedTemporaryFile(delete=False)
        state.save(temp.name)

        # Write bogus info to state
        state['list'] = 'foo'
        state['values.int'] = 43

        # This should only load the keys
        state.load(temp.name, lazy=True)

        self.assertEqual(len(state.keys()), 3)

        # This should raise an error
        shutil.move(temp.name, temp2.name)
        self.assertRaises(IOError, state.__getitem__, 'list')
        shutil.copyfile(temp2.name, temp.name)
        # Now it should work
        list_val = state['list']
        self.assertEqual(self.list_val, list_val)

        # This should raise another error
        shutil.move(temp.name, temp2.name)
        self.assertRaises(IOError, state.__getitem__, 'values.int')
        shutil.copyfile(temp2.name, temp.name)
        # This should work again
        int_val = state['values.int']
        self.assertEqual(self.int_val, int_val)

        os.remove(temp.name)
        os.remove(temp2.name)

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
                state['a'] = i ** 2
                state['b'] = i ** 3
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

    def test_saving_deleted_value(self):
        """Test saving really deletes entry
        """
        state['a'] = 12
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('a', state)
            state.load(temp.name)
            self.assertIn('a', state)
            del state['a']

            self.assertNotIn('a', state)
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('a', state)
            state.load(temp.name)
            self.assertNotIn('a', state)

    def test_saving_unloaded_value(self):
        """Test saving does not delete unloaded values
        """
        state['a'] = 12
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('a', state)
            state.load(temp.name)
            state['b'] = 12
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('a', state)
            self.assertNotIn('b', state)
            state.load(temp.name)
            self.assertIn('a', state)
            self.assertIn('b', state)


class TestStateEfficientIO(StateTester):
    """Test save/load functionality of pyexperiment's state for numpy arrays
    """
    def tearDown(self):
        """Clean up after tests
        """
        state.reset_instance()

    def test_saving_loading_np_array(self):
        """Test saving and loading a numpy array
        """
        random = np.random.rand(100)
        state['random'] = random
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('random', state)
            state.load(temp.name, lazy=False)
            self.assertTrue((random == state['random']).all())

    def test_saving_loading_np_array2(self):
        """Test saving and loading numpy arrays of higher dimension
        """
        random1 = np.random.rand(321, 123)
        random2 = np.random.randint(0, 100, (123, 345))
        state['random1'] = random1
        state['random2'] = random2
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('random1', state)
            self.assertNotIn('random2', state)
            state.load(temp.name, lazy=False)
            self.assertTrue((random1 == state['random1']).all())
            self.assertTrue((random2 == state['random2']).all())
            self.assertEqual(state['random1'].shape, random1.shape)
            self.assertEqual(state['random2'].shape, random2.shape)
            self.assertEqual(state['random1'].dtype, random1.dtype)
            self.assertEqual(state['random2'].dtype, random2.dtype)

    def test_saving_loading_lazy_array(self):
        """Test saving and loading a numpy array
        """
        random = np.random.rand(100)
        state['random'] = random
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            self.assertNotIn('random', state)
            state.load(temp.name)
            self.assertTrue((random == state['random']).all())


class TestStateHandler(unittest.TestCase):
    """Test the state's StateHandler
    """
    def tearDown(self):
        """Clean up after the test
        """
        state.reset_instance()

    def test_with_block_does_not_load(self):
        """Test the basic with-block of the StateHandler does not load anything
        """
        state['a'] = 1
        self.assertEqual(len(state), 1)
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            with StateHandler(temp.name):
                self.assertEqual(len(state), 0)

    def test_with_block_does_not_save(self):
        """Test the basic with-block of the StateHandler does not save anything
        """
        state['a'] = 1
        self.assertEqual(len(state), 1)
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            with StateHandler(temp.name):
                state['a'] = 42
            state.reset_instance()
            state.load(temp.name)
            self.assertEqual(state['a'], 1)

    def test_with_block_does_load(self):
        """Test the with-block of the StateHandler loads if required
        """
        state['a'] = 123
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            with StateHandler(temp.name, load=True):
                self.assertEqual(len(state), 1)
                self.assertEqual(state['a'], 123)

    def test_with_block_does_save(self):
        """Test the with-block of the StateHandler saves if required
        """
        state['a'] = 1
        with tempfile.NamedTemporaryFile() as temp:
            state.save(temp.name)
            state.reset_instance()
            with StateHandler(temp.name, save=True):
                state['a'] = 42
            state.reset_instance()
            state.load(temp.name)
            self.assertEqual(state['a'], 42)

    def test_with_block_locks(self):
        """Test the with-block of the StateHandler locks the state
        """
        state['a'] = 123
        with tempfile.NamedTemporaryFile() as temp:
            def other_op():
                """Function to run in another process"""
                StateHandler.STATE_LOCK_TIMEOUT = 0.001
                other_handler = StateHandler(temp.name, load=True)

                self.assertRaises(RuntimeError,
                                  other_handler.__enter__)

            state.save(temp.name)
            state.reset_instance()
            with StateHandler(temp.name, load=True):
                process = multiprocessing.Process(target=other_op)
                process.start()
                process.join()


if __name__ == '__main__':
    unittest.main()
