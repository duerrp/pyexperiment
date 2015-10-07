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
from six import StringIO

from pyexperiment import state
from pyexperiment.state_context import substate_context
from pyexperiment.state_context import thread_state_context
from pyexperiment.state_context import processing_state_context
from pyexperiment.utils.stdout_redirector import stdout_err_redirector


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

    def test_global_state(self):
        """Test setting, getting global state in sub-state context
        """
        with substate_context('test'):
            state['a.b'] = 123
            state['c.d.e'] = 345
            state['__foo'] = 42
            state['__bar.foo'] = 43

            self.assertEqual(state['a.b'], 123)
            self.assertEqual(state['c.d.e'], 345)
            self.assertEqual(state['__foo'], 42)
            self.assertEqual(state['__bar.foo'], 43)

        self.assertEqual(state['test.a.b'], 123)
        self.assertEqual(state['test.c.d.e'], 345)
        self.assertEqual(state['__foo'], 42)
        self.assertEqual(state['__bar.foo'], 43)
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

    def test_get_nonexisting(self):
        """Test getting an item of the state that does not exist
        """
        with substate_context('test'):
            self.assertRaises(KeyError, lambda: state['bla'])

    def test_iterate(self):
        """Test iterating over sub state
        """
        with substate_context('test'):
            state['a'] = 1
            state['b'] = 2
            for elem in state:
                if elem == 'a':
                    self.assertEqual(state[elem], 1)
                elif elem == 'b':
                    self.assertEqual(state[elem], 2)
                else:
                    assert False


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

    def test_delete_nonexisting(self):
        """Test deleting non-existing sub-state in threads
        """
        with thread_state_context():
            def worker():
                """thread worker function"""
                def dell():
                    """Test function"""
                    del state['foo']
                self.assertRaises(KeyError, dell)

            threads = []
            for _ in range(20):
                thread = threading.Thread(target=worker)
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

    def test_after_exception(self):
        """Test setting, getting state after exception in threads
        """
        state['a'] = 1
        buf_out = StringIO()
        buf_err = StringIO()
        try:
            with stdout_err_redirector(buf_out, buf_err):
                with thread_state_context():
                    def worker():
                        """thread worker function"""
                        raise RuntimeError

                    threads = []
                    for _ in range(20):
                        thread = threading.Thread(target=worker)
                        thread.start()
                        threads.append(thread)

                    for thread in threads:
                        thread.join()
                    raise RuntimeError
        except RuntimeError:
            pass
        self.assertEqual(state['a'], 1)


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


def worker4():
    """Process worker function, needs to be defined at top level"""
    try:
        state[[1, 2, 3]] = 12
    except TypeError:
        return True
    return False


def worker5():
    """Process worker function, needs to be defined at top level"""
    try:
        del state['bla']
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

    def test_raises_on_setting(self):
        """Test setting bad state in 4 processes
        """
        with processing_state_context():
            n_jobs = 200
            pool = multiprocessing.Pool(processes=4)
            results = []
            for _ in range(n_jobs):
                results.append(pool.apply_async(worker4))

            pool.close()
            pool.join()

        for i in range(n_jobs):
            self.assertTrue(results[i].get())

    def test_raises_on_deleting(self):
        """Test deleting bad state in 4 processes
        """
        with processing_state_context():
            n_jobs = 200
            pool = multiprocessing.Pool(processes=4)
            results = []
            for _ in range(n_jobs):
                results.append(pool.apply_async(worker5))

            pool.close()
            pool.join()

        for i in range(n_jobs):
            self.assertTrue(results[i].get())

    def test_after_exception(self):
        """Test deleting bad state in 4 processes
        """
        state['a'] = 12
        try:
            with processing_state_context():
                raise RuntimeError

        except RuntimeError:
            pass

        self.assertEqual(state['a'], 12)


if __name__ == '__main__':
    unittest.main()
