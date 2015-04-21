"""Tests the state module of pyexperiment

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import io
import logging

from pyexperiment import log
from pyexperiment import Logger


class TestLogger(unittest.TestCase):
    """Test basic logging
    """
    def setUp(self):
        """Setup test fixure
        """
        self.log_stream = io.StringIO()
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(self.log_stream)
        log.reset_instance()

    def tearDown(self):
        """Teardown test fixure
        """
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler()
        log.close()
        log.reset_instance()

    def test_fatal_console_logging(self):
        """Test the most basic console logging at the fatal level
        """
        log.initialize(console_level=logging.INFO)
        log.fatal("Test")
        log.close()
        # Something should be logged
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)

        log.initialize(console_level=logging.DEBUG)
        log.fatal("Test")
        log.close()
        # Something should be logged
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)

    def test_info_console_logging(self):
        """Test the most basic console logging at the fatal level
        """
        log.initialize(console_level=logging.FATAL)
        log.info("Test")
        log.close()
        # Something should be logged
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        log.initialize(console_level=logging.DEBUG)
        log.info("Test")
        log.close()
        # Something should be logged
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)

    def test_pre_init_logger(self):
        """Test that logging before initializing the logger works
        """
        log.fatal("Test")

        # Nothing should be logged yet
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        log.initialize()

        # Something should be logged here
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)
