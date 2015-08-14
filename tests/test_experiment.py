"""Tests the experiment module of pyexperiment

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import argparse
import io
import mock
import tempfile
import logging

from pyexperiment import experiment
from pyexperiment.utils.stdout_redirector import stdout_redirector
from pyexperiment import state
from pyexperiment import conf
from pyexperiment import Logger


class TestExperiment(unittest.TestCase):
    """Test the experiment module
    """
    def setUp(self):
        """Setup the test fixture
        """
        pass

    def tearDown(self):
        """Tear down the test fixture
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

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "custom_function"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertTrue(run[0])
        self.assertEqual(len(buf.getvalue()), 0)

    def test_main_shows_commands(self):
        """Test running main shows commands
        """
        def custom_function1():
            """User function
            """
            pass

        def custom_function2():
            """User function
            """
            pass

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "show_commands"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function1, custom_function2])

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r"custom_function1")
        self.assertRegexpMatches(buf.getvalue(), r"custom_function2")

    def test_main_not_enough_arguments(self):
        """Test running main without command
        """
        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main()

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r"[Nn]ot enough arguments")

    def test_main_does_not_run_function(self):
        """Test running main does not call unnecessary function but complains
        """
        run = [False]

        def custom_function():
            """User function
            """
            run[0] = True

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "help"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertFalse(run[0])
        self.assertNotEqual(len(buf.getvalue()), 0)

    def test_main_gives_help(self):
        """Test running help shows docstring
        """
        run = [False]

        def custom_function():
            """This should be printed!!
            """
            run[0] = True

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "help", "custom_function"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertFalse(run[0])
        self.assertIn("This should be printed!!", buf.getvalue())

    def test_main_complains_on_help(self):
        """Test running help complains on help for wrong command
        """
        def custom_function():
            """Foo function
            """
            pass

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "help", "foo"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertRegexpMatches(buf.getvalue(), r"[cC]ommand")
        self.assertRegexpMatches(buf.getvalue(), r"not")
        self.assertRegexpMatches(buf.getvalue(), r"foo")

    def test_main_runs_test(self):
        """Test running main calls tests when needed
        """
        class ExampleTest(unittest.TestCase):
            """Test case for the test
            """
            pass

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "test"]

        with mock.patch.object(unittest, 'TextTestRunner') as mock_method:
            experiment.main(commands=[], tests=[ExampleTest])
        self.assertEqual(mock_method.call_count, 1)

    def test_main_shows_test(self):
        """Test running main shows tests when needed
        """
        class ExampleTest(unittest.TestCase):
            """Test case for the test
            """
            pass

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "show_tests"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(tests=[ExampleTest])

        self.assertRegexpMatches(buf.getvalue(), r"ExampleTest")

    def test_main_doesnt_test_on_help(self):
        """Test running main does not call tests when not needed
        """
        class ExampleTest(unittest.TestCase):
            """Test case for the test
            """
            pass

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-h"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            with mock.patch.object(unittest, 'TextTestRunner') as mock_method:
                try:
                    experiment.main(commands=[], tests=[ExampleTest])
                    self.assertEqual(mock_method.call_count, 0)
                except SystemExit:
                    pass

    @mock.patch('pyexperiment.experiment.embed_interactive')
    def test_main_runs_interactive(self, mock_interactive):
        """Test running main runs interactive session
        """
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "--interactive"]

        experiment.main(commands=[], tests=[])
        self.assertTrue(mock_interactive.call_count == 1)

    def test_main_shows_empty_state(self):
        """Test running main shows empty state
        """
        with tempfile.NamedTemporaryFile() as temp:
            state['bla'] = 12
            del state['bla']
            state.save(temp.name)

            spec = ('[pyexperiment]\n'
                    'state_filename = string(default=%s)' % temp.name)
            # Monkey patch arg parser
            argparse._sys.argv = [  # pylint: disable=W0212
                "test", "show_state"]

            buf = io.StringIO()
            with stdout_redirector(buf):
                experiment.main(config_spec=spec)
            self.assertRegexpMatches(buf.getvalue(), r"[Ss]tate empty")

    def test_main_shows_default_state(self):
        """Test running main shows the default state
        """
        with tempfile.NamedTemporaryFile() as temp:
            state['bla'] = 12
            state.save(temp.name)

            spec = ('[pyexperiment]\n'
                    'state_filename = string(default=%s)' % temp.name)
            # Monkey patch arg parser
            argparse._sys.argv = [  # pylint: disable=W0212
                "test", "show_state"]

            buf = io.StringIO()
            with stdout_redirector(buf):
                experiment.main(config_spec=spec)
            self.assertRegexpMatches(buf.getvalue(), r"bla")
            self.assertRegexpMatches(buf.getvalue(), r"12")

    def test_main_shows_other_state(self):
        """Test running main shows state from file
        """
        with tempfile.NamedTemporaryFile() as temp:
            state['foo'] = 42
            state.save(temp.name)

            # Monkey patch arg parser
            argparse._sys.argv = [  # pylint: disable=W0212
                "test", "show_state", temp.name]

            buf = io.StringIO()
            with stdout_redirector(buf):
                experiment.main()
            self.assertRegexpMatches(buf.getvalue(), r"foo")
            self.assertRegexpMatches(buf.getvalue(), r"42")

    def test_main_overrides_option(self):
        """Test running main called with -o works as expected
        """
        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True
            self.assertEqual(conf['bla'], 'foo')

        conf['bla'] = 'bla'
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-o", "bla", "foo", "foo_fun"]

        self.assertFalse(called[0])

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['bla'], 'foo')

    def test_main_overrides_verbosity(self):
        """Test running main called with --verbosity works as expected
        """
        log_stream = io.StringIO()
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(log_stream)

        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "--verbosity", "DEBUG", "foo_fun"]

        self.assertFalse(called[0])

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.verbosity'], 'DEBUG')

        called[0] = False
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "--verbosity", "WARNING", "foo_fun"]

        self.assertFalse(called[0])

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.verbosity'], 'WARNING')

    def test_main_verbosity_debug(self):
        """Test running main called with -v works as expected
        """
        log_stream = io.StringIO()
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(log_stream)

        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-v", "foo_fun"]

        self.assertFalse(called[0])

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.verbosity'], 'DEBUG')
