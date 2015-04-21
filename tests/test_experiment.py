"""Tests the experiment module of pyexperiment

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import argparse
import sys
import io

from pyexperiment import experiment
from pyexperiment.utils.stdout_redirector import stdout_redirector, \
    stdout_err_redirector


class TestExperiment(unittest.TestCase):
    """Test the experiment module
    """
    def setUp(self):
        """Setup the test fixure
        """
        pass

    def tearDown(self):
        """Tear down the test fixure
        """
        pass

    def test_main_runs_function(self):
        """Test running main calls function
        """
        run = [False]

        def custom_function():
            """User function
            """
            run[0] = True

        # Need to monkey patch arg parser here
        argparse._sys.argv = ["test", "custom_function"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertTrue(run[0])
        self.assertEqual(len(buf.getvalue()), 0)

    def test_main_does_not_run_function(self):
        """Test running main does not call unnecessary function but complains
        """
        run = [False]

        def custom_function():
            """User function
            """
            run[0] = True

        # Need to monkey patch arg parser here
        argparse._sys.argv = ["test", "help"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertFalse(run[0])
        self.assertNotEqual(len(buf.getvalue()), 0)

    def test_main_gives_help(self):
        """Test running help shows docstring
        """
        run = [False]

        def custom_function():
            """This should be printed!!
            """
            run[0] = True

        # Need to monkey patch arg parser here
        argparse._sys.argv = ["test", "help", "custom_function"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertFalse(run[0])
        self.assertIn("This should be printed!!", buf.getvalue())

    # Need to mock unittest to avoid printing
    # def test_main_runs_test(self):
    #     """Test running main calls tests
    #     """
    #     run = [False]

    #     class ExampleTest(unittest.TestCase):
    #         pass
    #     #     """Test case for the test
    #     #     """
    #     #     def custom_test(self):
    #     #         """Test something
    #     #         """
    #     #         run[0] = True

    #     # # Need to monkey patch arg parser and stdout here
    #     argparse._sys.argv = ["test", "test"]

    #     buf_out, buf_err = io.StringIO(), io.StringIO()
    #     with stdout_err_redirector(buf_out, buf_err):
    #         experiment.main(commands=[], tests=[ExampleTest])
