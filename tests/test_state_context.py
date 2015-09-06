"""Tests the substate_context

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import threading
import multiprocessing

from pyexperiment import state
from pyexperiment.state_context import substate_context
from pyexperiment.state_context import thread_state_context
from pyexperiment.state_context import processing_state_context


class TestSubStateContext(unittest.TestCase):
    """Test the substate_context
    """
    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def test_set_get_first_level(self):
        """Test setting, getting sub-state at the lowest level
        """
        with substate_context('test'):
            state['a'] = 123
            self.assertEqual(state['a'], 123)

        self.assertEqual(state['test.a'], 123)
        self.assertRaises(KeyError, state.__getitem__, 'a')

    def test_set_get_higher_levels(self):
        """Test setting, getting sub-state at the higher levels
        """
        with substate_context('test'):
            state['a.b'] = 123
            state['c.d.e'] = 345

            self.assertEqual(state['a.b'], 123)
            self.assertEqual(state['c.d.e'], 345)

        self.assertEqual(state['test.a.b'], 123)
        self.assertEqual(state['test.c.d.e'], 345)
        self.assertRaises(KeyError, state.__getitem__, 'a.b')
        self.assertRaises(KeyError, state.__getitem__, 'c.d.e')

    def test_get_section(self):
        """Test getting a section of the state
        """
        with substate_context('test'):
            state['a.a'] = 12
            state['a.b'] = 13

            self.assertIn('a', state)
            self.assertIn('a.a', state)
            self.assertIn('a.b', state)
            self.assertEqual(state['a.a'], 12)
            self.assertEqual(state['a.b'], 13)


class TestThreadStateContext(unittest.TestCase):
    """Test the thread_state_context
    """
    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def test_basic_functionality(self):
        """Test setting, getting sub-state in 20 threads
        """
        with thread_state_context():
            def worker(i):
                """thread worker function"""
                state[str(i)] = i
                self.assertEqual(state[str(i)], i)

            threads = []
            for i in range(20):
                thread = threading.Thread(target=worker, args=(i,))
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            for i in range(len(threads)):
                self.assertEqual(state[str(i)], i)


def worker1(i):
    """Process worker function, needs to be defined at top level"""
    state[str(i)] = i
    if not state[str(i)] == i:
        return False
    else:
        return True


def worker2(i):
    """Process worker function, needs to be defined at top level"""
    state[str(i)] = 'bla'
    del state[str(i)]


def worker3(i):
    """Process worker function, needs to be defined at top level"""
    try:
        _ = state[str(i)]
    except KeyError:
        return True
    return False


class TestProcessingStateContext(unittest.TestCase):
    """Test the processing_state_context
    """
    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def test_basic_functionality(self):
        """Test setting, getting state in 4 processes
        """
        with processing_state_context():
            n_jobs = 2
            pool = multiprocessing.Pool(processes=4)
            results = []
            for i in range(n_jobs):
                results.append(pool.apply_async(worker1, (i,)))

            pool.close()
            pool.join()

        for i in range(n_jobs):
            self.assertTrue(results[i].get())
            self.assertEqual(state[str(i)], i)

    def test_deleting(self):
        """Test deleting state in 4 processes
        """
        with processing_state_context():
            n_jobs = 2
            pool = multiprocessing.Pool(processes=4)
            results = []
            for i in range(n_jobs):
                results.append(pool.apply_async(worker2, (i,)))

            pool.close()
            pool.join()

        for i in range(n_jobs):
            self.assertNotIn(str(i), state)

    def test_raises_on_getting(self):
        """Test getting non-existing state in 4 processes
        """
        with processing_state_context():
            n_jobs = 200
            pool = multiprocessing.Pool(processes=4)
            results = []
            for i in range(n_jobs):
                results.append(pool.apply_async(worker3, (i,)))

            pool.close()
            pool.join()

        for i in range(n_jobs):
            self.assertTrue(results[i].get())


if __name__ == '__main__':
    unittest.main()
