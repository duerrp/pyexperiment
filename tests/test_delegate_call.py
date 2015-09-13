"""Tests the utils.DelegateCall module of pyexperiment

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import multiprocessing
from six import StringIO
import os
import unittest

from pyexperiment.utils.DelegateCall import DelegateCall
from pyexperiment.utils.stdout_redirector import stdout_err_redirector


class TestDelegateCall(unittest.TestCase):
    """Tests the DelegateCall object
    """
    def test_delegating_same_process(self):
        """Test delegating a call from the same process
        """
        called = [0]

        def target():
            """Target function"""
            called[0] += 1

        delegated = DelegateCall(target)
        self.assertEqual(called[0], 0)
        delegated()
        delegated.join()
        self.assertEqual(called[0], 1)

    def test_delegating_exception(self):
        """Test delegating a call from the same process with an exception
        """
        called = [0]

        _buf_out = StringIO()
        buf_err = StringIO()
        with stdout_err_redirector(_buf_out, buf_err):
            def target():
                """Target function"""
                called[0] += 1
                raise RuntimeError()

            delegated = DelegateCall(target)
            self.assertEqual(called[0], 0)
            delegated()
            delegated.join()

        self.assertEqual(called[0], 1)
        self.assertRegexpMatches(buf_err.getvalue(), 'RuntimeError')

    def test_delegating_other_process(self):
        """Test delegating a call from another process
        """
        called = [0]
        called_from = []

        def target():
            """Target function"""
            called[0] += 1
            called_from.append(os.getpid())

        delegated = DelegateCall(target)

        def process_target():
            """Sub-process
            """
            delegated()

        process = multiprocessing.Process(target=process_target)
        self.assertEqual(called[0], 0)
        process.start()
        process.join()
        delegated.join()
        self.assertEqual(called[0], 1)
        self.assertEqual(called_from[0], os.getpid())


if __name__ == '__main__':
    unittest.main()
