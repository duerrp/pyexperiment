"""Tests replicating

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import numpy as np
# import logging
# import io
if True:  # Ugly, but makes pylint happy
    # pylint:disable=import-error
    from six.moves import range  # pylint: disable=redefined-builtin

from pyexperiment import state
# from pyexperiment import Logger
# from pyexperiment import log
# from pyexperiment.utils.stdout_redirector import stdout_err_redirector
from pyexperiment.replicate import replicate, collect_results
from pyexperiment.replicate import SUBSTATE_KEY_PATTERN

FAKE_ERROR = RuntimeError("Foo")
"""Fake error for testing
"""


def experiment():
    """Test experiment, needs to be defined at top level for multiprocessing
    """
    state['result'] = "bla"


def experiment2():
    """Test experiment, needs to be defined at top level for multiprocessing
    """
    state['result'] = "bla"
    _bla = state['result']
    del state['result']


def experiment3():
    """Test experiment, needs to be defined at top level for multiprocessing
    """
    raise FAKE_ERROR


def experiment4():
    """Test experiment, needs  to be defined at top level for multiprocessing
    """
    np.random.seed()
    state['result'] = np.random.rand(1)


class TestReplicate(unittest.TestCase):
    """Test the replicate function, serial and parallel
    """
    def tearDown(self):
        """Teardown test fixture
        """
        state.reset_instance()

    def test_setting_state(self):
        """Test setting
        """
        no_replicates = 25

        replicate(experiment, no_replicates)
        for i in range(no_replicates):
            self.assertIn('result', state[SUBSTATE_KEY_PATTERN % i])
            self.assertEqual(state[SUBSTATE_KEY_PATTERN % i]['result'], "bla")

    def test_getting_state(self):
        """Test getting
        """
        no_replicates = 25

        replicate(experiment2, no_replicates)
        for i in range(no_replicates):
            self.assertNotIn('result', state[SUBSTATE_KEY_PATTERN % i])

    def test_raises(self):
        """Test raising exception in replicate
        """
        no_replicates = 25
        try:
            replicate(experiment3, no_replicates)
        except RuntimeError as err:
            self.assertEqual(err, FAKE_ERROR)
        else:
            assert False

    def test_setting_state_parallel(self):
        """Test setting in parallel
        """
        no_replicates = 25

        replicate(experiment, no_replicates, parallel=True, no_processes=2)
        for i in range(no_replicates):
            self.assertIn('result', state[SUBSTATE_KEY_PATTERN % i])
            self.assertEqual(state[SUBSTATE_KEY_PATTERN % i]['result'], "bla")

    def test_getting_state_parallel(self):
        """Test getting in parallel
        """
        no_replicates = 25
        replicate(experiment2, no_replicates, parallel=True, no_processes=2)
        for i in range(no_replicates):
            self.assertNotIn(SUBSTATE_KEY_PATTERN % i + '.result', state)

    # Does not work properly yet
    # def test_raises_parallel(self):
    #     """Test raising exception in parallel (should log error)
    #     """
    #     log_stream = io.StringIO()
    #     buf_out = io.StringIO()
    #     buf_err = io.StringIO()
    #     Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(log_stream)
    #     log.reset_instance()
    #     log.initialize(console_level=logging.ERROR)
    #     no_replicates = 2
    #     with stdout_err_redirector(buf_out, buf_err):
    #         try:
    #             replicate(experiment3, no_replicates, parallel=True)
    #         except:
    #             pass
    #     log.close()
    #     # Should have logged errors
    #     # self.assertNotEqual(len(log_stream.getvalue()), 0)
    #     print("log", log_stream.getvalue())
    #     print("out", buf_out.getvalue())
    #     print("err", buf_err.getvalue())

    def test_collecting(self):
        """Test collecting results
        """
        no_replicates = 25

        replicate(experiment4, no_replicates)
        for i in range(no_replicates):
            self.assertIn('result', state[SUBSTATE_KEY_PATTERN % i])

        results = collect_results('result', no_replicates=no_replicates)
        self.assertEqual(len(results), no_replicates)
        for i, r_1 in enumerate(results):
            for k, r_2 in enumerate(results):
                if not i == k:
                    self.assertFalse((r_1 == r_2).all())

    def test_collecting_parallel(self):
        """Test collecting results
        """
        no_replicates = 25

        replicate(experiment4, no_replicates, parallel=True, no_processes=2)
        for i in range(no_replicates):
            self.assertIn('result', state[SUBSTATE_KEY_PATTERN % i])

        results = collect_results('result', no_replicates=no_replicates)
        self.assertEqual(len(results), no_replicates)
        for i, r_1 in enumerate(results):
            for k, r_2 in enumerate(results):
                if not i == k:
                    self.assertFalse((r_1 == r_2).all())


if __name__ == '__main__':
    unittest.main()
