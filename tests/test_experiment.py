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

from pyexperiment import experiment
from pyexperiment.utils.stdout_redirector import stdout_redirector
from pyexperiment import state


class TestExperiment(unittest.TestCase):
    """Test the experiment module
    """
    def setUp(self):
        """Setup the test fixure
        """
        pass

    def tearDown(self):
        """Tear down the test fixure
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
