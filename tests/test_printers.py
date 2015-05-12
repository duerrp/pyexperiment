"""Tests the utils.printers module of pyexperiment

Written by Peter Duerr

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import io
import re

from pyexperiment.utils.stdout_redirector import stdout_redirector
from pyexperiment.utils import printers


class PrinterTest(object):
    """ABC for the printer tests
    """
    COLOR_SEQ = None
    """The color sequence of the tested color, set by the subclass
    """

    def printer(self, messsage, *args):
        """Subclasses should implement this
        """
        raise NotImplementedError

    def test_reset_seqence_appears(self):
        """Test printing actually produces the reset sequence
        """
        buf = io.StringIO()
        with stdout_redirector(buf):
            self.printer("foo")

        # We will get the assertion later (by  dependency injection)
        self.assertRegexpMatches(  # pylint: disable=no-member
            buf.getvalue(),
            "%s" % re.escape(printers.RESET_SEQ))

    def test_color_sequence_appears(self):
        """Test printing actually produces the color sequence
        """
        buf = io.StringIO()
        with stdout_redirector(buf):
            self.printer("foo")

        # We will get the assertion later (by dependency injection)
        # pylint: disable=no-member
        self.assertIsNotNone(self.COLOR_SEQ)
        self.assertRegexpMatches(
            buf.getvalue(),
            "%s" % re.escape(self.COLOR_SEQ))

    def test_message_sequence_appears(self):
        """Test printing actually prints the message
        """
        buf = io.StringIO()
        with stdout_redirector(buf):
            self.printer("foo")

        # We will get the assertion later (by dependency injection)
        self.assertRegexpMatches(  # pylint: disable=no-member
            buf.getvalue(), "foo")

    def test_message_interpolates_args(self):
        """Test printing actually interpolates the arguments correctly
        """
        message = "str: %s, int: %d, float %f"
        arguments = ('bla', 12, 3.14)
        buf = io.StringIO()
        with stdout_redirector(buf):
            self.printer(message, *arguments)

        # We will get the assertion later (by dependency injection)
        self.assertRegexpMatches(  # pylint: disable=no-member
            buf.getvalue(), r'.*%s.*' % (message % arguments))


def create_printer_test(color_):
    """Factory for printer tests
    """
    class TestPrinters(unittest.TestCase, PrinterTest):
        """Test the printer for a color
        """
        COLOR_SEQ = printers.COLORS[color_]
        """The color sequence of the tested color
        """

        def printer(self, message, *args):
            """The printer to be tested
            """
            getattr(printers, 'print_' + color_)(message, *args)

    return TestPrinters

for color in printers.COLORS.keys():
    vars()['Test' + color.title()] = create_printer_test(color)
