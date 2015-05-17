"""Tests the utils.plot module of pyexperiment

Written by Peter Duerr

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import mock
from multiprocessing import Queue
from threading import Thread
from time import sleep

from pyexperiment.utils import plot


class TestPlot(unittest.TestCase):
    """Test the plot module
    """
    def tearDown(self):
        """Tear down the test fixture
        """
        # Some tests may leave pl 'configured'
        plot._SETUP_DONE = False  # pylint: disable=protected-access

    def test_setup_does_not_override(self):
        """Test setting up plotting
        """
        self.assertTrue(plot.setup_plotting(override_setup=False))
        self.assertFalse(plot.setup_plotting(override_setup=False))

    def test_setup_does_override(self):
        """Test setting up plotting with override
        """
        self.assertTrue(plot.setup_plotting(override_setup=True))
        self.assertTrue(plot.setup_plotting(override_setup=True))

    def test_setup_figure(self):
        """Test setting up a figure
        """
        fig = plot.setup_figure()
        self.assertIsNotNone(fig)

    def test_setup_fig_setup_plotting(self):
        """Test setting up a figure sets up plotting as well
        """
        _fig = plot.setup_figure()
        self.assertFalse(plot.setup_plotting(override_setup=False))


class TestAsyncPlot(unittest.TestCase):
    """Test the AsyncPlot
    """
    def tearDown(self):
        """Tear down the test fixture
        """
        # Some tests may leave plotting 'configured'
        plot._SETUP_DONE = False  # pylint: disable=protected-access

    def test_starts_process(self):
        """Tests that AsyncPlot starts a process
        """
        with mock.patch('pyexperiment.utils.plot.Process') as process:
            _async = plot.AsyncPlot()

        self.assertTrue(process.called)
        self.assertIn('target', process.call_args[1])

    def test_plot_process_closes(self):
        """Tests the process itself (without multiprocessing)
        """
        async = plot.AsyncPlot()
        async.close()
        self.assertFalse(async.process.is_alive())
        async.process.join()

    def test_plot_process_plot(self):
        """Tests the plot methods adds to queue
        """
        with mock.patch('pyexperiment.utils.plot.Process') as _process:
            with mock.patch('pyexperiment.utils.plot.Queue') as queue:
                async = plot.AsyncPlot()
                async.plot("a", "b", "c")
                async.plot(2, [1, 2])

        self.assertEqual(queue.mock_calls[0], mock.call())
        self.assertEqual(queue.mock_calls[1], mock.call().put(("a", "b", "c")))
        self.assertEqual(queue.mock_calls[2], mock.call().put((2, [1, 2])))

    def test_plot_process_target(self):
        """Tests the target function of the process synchronously
        """
        queue = Queue()
        queue.put((1, 2, 'k'))

        def drop_poison_pill():
            """Puts None on the queue after it is empty
            """
            while not queue.empty():
                sleep(0.01)
            sleep(0.01)
            queue.put(None)

        Thread(target=drop_poison_pill).start()
        with mock.patch('pyexperiment.utils.plot.plt') as plt:
            plot.AsyncPlot.plot_process(queue, name="test_plot")

        self.assertTrue(plot._SETUP_DONE)  # pylint: disable=protected-access
        self.assertIn(mock.call.figure(), plt.mock_calls)
        self.assertIn(mock.call.plot(1, 2, 'k'), plt.mock_calls)
