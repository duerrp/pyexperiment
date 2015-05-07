"""Tests the interactive utilities

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import mock
import six
import sys

from pyexperiment.utils.interactive import embed_interactive


class TestInteractive(unittest.TestCase):
    """Test the interactive utilities
    """
    def test_calling_ipython(self):
        """Test calling embed_interactive calls ipython 3.0 if available
        """
        my_python = mock.MagicMock()
        embed = mock.MagicMock()
        my_python.__version__ = '3.0.0'
        my_python.embed = embed
        sys.modules['IPython'] = my_python

        embed_interactive()

        self.assertTrue(embed.called)
        # New IPython should not be called with user_ns but local_ns
        self.assertNotIn('user_ns', embed.call_args[1])
        self.assertIn('local_ns', embed.call_args[1])

    def test_calling_old_ipython(self):
        """Test calling embed_interactive calls old ipython if available
        """
        my_python = mock.MagicMock()
        embed = mock.MagicMock()
        my_python.__version__ = '1.2.1'
        my_python.embed = embed
        sys.modules['IPython'] = my_python

        embed_interactive()

        self.assertTrue(embed.called)
        # Old IPython should be called with user_ns not local_ns
        self.assertIn('user_ns', embed.call_args[1])
        self.assertNotIn('local_ns', embed.call_args[1])

    def test_calling_without_ipython(self):
        """Test calling embed_interactive when no IPython is around
        """
        try:
            import builtins
        except ImportError:
            import __builtin__ as builtins

        realimport = builtins.__import__

        def myimport(*args):
            """Monkey patch import"""
            if args[0] in 'IPython':
                raise ImportError
            return realimport(*args)

        my_python = mock.MagicMock()

        if six.PY2:
            builtins_name = '__builtin__.__import__'
        if six.PY3:
            builtins_name = 'builtins.__import__'

        with mock.patch(builtins_name, myimport):
            with mock.patch('code.InteractiveConsole', my_python):
                embed_interactive()

        self.assertTrue(my_python.called)
