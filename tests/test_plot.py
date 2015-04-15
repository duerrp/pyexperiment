"""Tests the utils.plot module of pyexperiment

Written by Peter Duerr
"""

import unittest

from pyexperiment.utils import plot


class TestPlot(unittest.TestCase):
    """Test the plot module
    """
    def setUp(self):
        """Setup the test fixure
        """
        pass

    def tearDown(self):
        """Tear down the test fixure
        """
        pass

    def test_setup_matplotlib(self):
        """Test setting up matplotlib
        """
        plot.setup_matplotlib()
        # TODO: more checks here?

    def test_setup_figure(self):
        """Test setting up a fiugre
        """
        fig = plot.setup_figure()
        self.assertIsNotNone(fig)
