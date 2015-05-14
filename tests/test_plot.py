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
    def tearDown(self):
        """Tear down the test fixture
        """
        # Some tests may leave matplotlib 'configured'
        plot._SETUP_DONE = False  # pylint: disable=protected-access

    def test_setup_does_not_override(self):
        """Test setting up matplotlib
        """
        self.assertTrue(plot.setup_matplotlib(override_setup=False))
        self.assertFalse(plot.setup_matplotlib(override_setup=False))

    def test_setup_does_override(self):
        """Test setting up matplotlib
        """
        self.assertTrue(plot.setup_matplotlib(override_setup=True))
        self.assertTrue(plot.setup_matplotlib(override_setup=True))

    def test_setup_figure(self):
        """Test setting up a figure
        """
        fig = plot.setup_figure()
        self.assertIsNotNone(fig)

    def test_setup_fig_setup_matplotlib(self):
        """Test setting up a figure sets up matplotlib as well
        """
        _fig = plot.setup_figure()
        self.assertFalse(plot.setup_matplotlib(override_setup=False))
