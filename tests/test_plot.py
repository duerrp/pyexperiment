"""Tests the utils.plot module of pyexperiment

Written by Peter Duerr

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest

from pyexperiment.utils import plot


class TestPlot(unittest.TestCase):
    """Test the plot module
    """
    def setUp(self):
        """Setup the test fixture
        """
        pass

    def tearDown(self):
        """Tear down the test fixture
        """
        pass

    def test_setup_matplotlib(self):
        """Test setting up matplotlib returns
        """
        self.assertIsNone(plot.setup_matplotlib())

    def test_setup_figure(self):
        """Test setting up a fiugre
        """
        fig = plot.setup_figure()
        self.assertIsNotNone(fig)
