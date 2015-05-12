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
import tempfile
import os

from pyexperiment import log
from pyexperiment import Logger
from pyexperiment.utils.stdout_redirector import stdout_redirector


class TestLogger(unittest.TestCase):
    """Test basic logging
    """
    def setUp(self):
        """Setup test fixture
        """
        self.log_stream = io.StringIO()
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(self.log_stream)
        log.reset_instance()

    def tearDown(self):
        """Teardown test fixture
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

    def test_file_logger_writes_to_file(self):
        """Test logging to file writes something to the log file
        """
        with tempfile.NamedTemporaryFile() as temp:
            log.initialize(filename=temp.name, no_backups=0)
            log.fatal("Test")
            log.close()

            # Make sure file exists
            self.assertTrue(os.path.isfile(temp.name))

            lines = temp.readlines()
            # There should be exactly one line in the file now
            self.assertEqual(len(lines), 1)

    def test_timing_logger_logs(self):
        """Test timing code logs a message
        """
        # Nothing should be logged yet
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        log.initialize()
        # Still, nothing should be logged yet
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        with log.timed(level=logging.FATAL):
            _ = 1 + 1
        log.close()
        # Something should be logged
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)

    def test_print_timings_prints(self):
        """Test timing code and printing really prints a message
        """
        buf = io.StringIO()

        # Nothing should be logged yet
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        log.initialize()
        # Still, nothing should be logged yet
        self.assertEqual(len(self.log_stream.getvalue()), 0)

        with log.timed(level=logging.FATAL):
            _ = 1 + 1

        with stdout_redirector(buf):
            log.print_timings()

        # Something should be printed
        self.assertNotEqual(len(buf.getvalue()), 0)

        log.close()
        # Something should be logged
        self.assertNotEqual(len(self.log_stream.getvalue()), 0)
