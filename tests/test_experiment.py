"""Tests the conf module of pyexperiment

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import argparse
import sys

from pyexperiment import experiment


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
        experiment.main(commands=[custom_function])

        self.assertTrue(run[0])
