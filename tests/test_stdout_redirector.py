"""Tests the stdout_redirector module of pyexperiment.utils

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import io
import sys

from pyexperiment.utils.stdout_redirector import stdout_redirector, \
    stdout_err_redirector


class TestStdoutRedirector(unittest.TestCase):
    """Test the stdout_redirector module
    """
    def setUp(self):
        """Setup the test fixure
        """
        pass

    def tearDown(self):
        """Tear down the test fixure
        """
        pass

    def test_captures_stdout(self):
        """Test capturing stdout from print
        """
        message = "This should be captured..."

        buf = io.StringIO()
        with stdout_redirector(buf):
            print(message)

        self.assertEqual(buf.getvalue(), message + '\n')

    def test_captures_stdout_stderr(self):
        """Test capturing stdout and stderr from print
        """
        message1 = "This should be captured on stdout..."
        message2 = "And this should be captured on stderr..."

        buf_out = io.StringIO()
        buf_err = io.StringIO()

        with stdout_err_redirector(buf_out, buf_err):
            print(message1)
            print(message2, file=sys.stderr)

        self.assertEqual(buf_out.getvalue(), message1 + '\n')
        self.assertEqual(buf_err.getvalue(), message2 + '\n')
