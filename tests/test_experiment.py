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
import multiprocessing

from pyexperiment import experiment
from pyexperiment.utils.stdout_redirector import stdout_redirector
from pyexperiment import state
from pyexperiment import conf
from pyexperiment import Logger
from pyexperiment import log


class TestExperimentBasic(unittest.TestCase):
    """Test the experiment module's basic functions
    """
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

    def test_main_prints_result(self):
        """Test running main prints the result of a function
        """
        def custom_function():
            """User function
            """
            return "Foo"

        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "custom_function"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[custom_function])

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r'Foo')

    def test_main_shows_commands(self):
        """Test running main shows commands
        """
        def default_function():
            """Default function
            """
            pass

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
            experiment.main(default=default_function,
                            commands=[custom_function1, custom_function2])

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r"default_function")
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

    def test_main_runs_default(self):
        """Test running main with default command
        """
        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test"]

        run = [False]

        def custom_function():
            """User function
            """
            run[0] = True

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(default=custom_function)

        self.assertEqual(len(buf.getvalue()), 0)
        self.assertTrue(run[0])

    def test_main_complains_default(self):
        """Test running main with default command taking an argument
        """
        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test"]

        def custom_function(_argument):
            """User function that takes an argument
            """
            pass

        self.assertRaises(
            TypeError,
            experiment.main,
            default=custom_function)

    def test_main_runs_other_function(self):
        """Test running main with default command and other function
        """
        # Monkey patch arg parser here
        argparse._sys.argv = [  # pylint: disable=W0212
            "test",
            "custom_function2"]

        run = [False, False]

        def custom_function():
            """User function
            """
            run[0] = True

        def custom_function2():
            """User function2
            """
            run[1] = True

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(default=custom_function,
                            commands=[custom_function2])

        self.assertEqual(len(buf.getvalue()), 0)
        self.assertFalse(run[0])
        self.assertTrue(run[1])

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

    def test_main_shows_no_test(self):
        """Test running main complains if there are no tests
        """
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "show_tests"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(tests=[])

        self.assertRegexpMatches(buf.getvalue(), r"No tests available")

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

    def test_main_shows_config(self):
        """Test running main shows the configuration
        """
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "show_config"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main()
        self.assertRegexpMatches(buf.getvalue(), r"\[pyexperiment\]")
        self.assertRegexpMatches(buf.getvalue(), r"n_processes")

    def test_main_saves_config(self):
        """Test running main saves the configuration
        """
        with tempfile.NamedTemporaryFile() as temp:
            # Monkey patch arg parser
            argparse._sys.argv = [  # pylint: disable=W0212
                "test", "save_config", temp.name]

            buf = io.StringIO()
            with stdout_redirector(buf):
                experiment.main()

            lines = open(temp.name).readlines()
            self.assertNotEqual(len(lines), 0)
            self.assertRegexpMatches("".join(lines), r"\[pyexperiment\]")
            self.assertRegexpMatches("".join(lines), r"n_processes")

            self.assertRegexpMatches(buf.getvalue(), r'Wrote configuration')


class TestExperimentOverrides(unittest.TestCase):
    """Test the experiment module's option overriding
    """
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

    def test_main_no_processes_default(self):
        """Test running main called without -j works as expected
        """
        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "foo_fun"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.n_processes'],
                         multiprocessing.cpu_count())

    def test_main_no_processes_simple(self):
        """Test running main called with -j works as expected
        """
        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-j", "42", "foo_fun"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.n_processes'],
                         42)

    def test_main_no_processes_long(self):
        """Test running main called with --processes works as expected
        """
        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True
        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "--processes", "44", "foo_fun"]

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.n_processes'],
                         44)


class TestExperimentLogging(unittest.TestCase):
    """Test the experiment's logging context
    """
    def setUp(self):
        """Set up the test
        """
        self.log_stream = io.StringIO()
        Logger.CONSOLE_STREAM_HANDLER = logging.StreamHandler(self.log_stream)

        log.reset_instance()
        conf.reset_instance()

    def test_main_logs_console(self):
        """Test running main logs as expected
        """
        argparse._sys.argv = [  # pylint: disable=W0212
            "test"]

        def hello():
            """Logs a message
            """
            log.fatal("Hello")

        experiment.main(default=hello)

        self.assertNotEqual(len(self.log_stream.getvalue()), 0)
        self.assertRegexpMatches(self.log_stream.getvalue(), r'Hello')

    def test_main_prints_timings(self):
        """Test running main logs timings as expected
        """
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-o", "pyexperiment.print_timings", "True"]

        def hello():
            """Logs a message
            """
            with log.timed("bla"):
                pass

        buf = io.StringIO()
        with stdout_redirector(buf):
            experiment.main(default=hello)

        self.assertNotEqual(len(buf.getvalue()), 0)
        self.assertRegexpMatches(buf.getvalue(), r'bla')

    def test_main_logs_file(self):
        """Test running main logs as expected
        """
        conf['pyexperiment.rotate_n_logs'] = 0
        argparse._sys.argv = [  # pylint: disable=W0212
            "test"]

        def hello():
            """Logs a message
            """
            log.debug("Hello")

        with tempfile.NamedTemporaryFile() as temp:
            conf['pyexperiment.log_filename'] = temp.name
            conf['pyexperiment.log_to_file'] = True
            experiment.main(default=hello)

            lines = open(temp.name).readlines()
            self.assertNotEqual(len(lines), 0)
            self.assertRegexpMatches("".join(lines), r'Hello')

        self.assertEqual(len(self.log_stream.getvalue()), 0)

    def test_main_verbosity_debug(self):
        """Test running main called with -v works as expected
        """
        called = [False]

        def foo_fun():
            """Foo function
            """
            called[0] = True

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "-v", "foo_fun"]

        self.assertFalse(called[0])

        experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.verbosity'], 'DEBUG')

    def test_main_overrides_verbosity(self):
        """Test running main called with --verbosity works as expected
        """
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

        experiment.main(commands=[foo_fun])

        self.assertTrue(called[0])
        self.assertEqual(conf['pyexperiment.verbosity'], 'WARNING')

    def test_logger_after_exception(self):
        """Test logger closing correctly after exception
        """
        # Monkey patch log closing
        close_old = Logger.Logger.close
        called = [False]

        def close(self):
            """Close the logger and record it"""
            close_old(self)
            called[0] = True

        Logger.Logger.close = close

        def foo_fun():
            """Foo function
            """
            raise RuntimeError

        # Monkey patch arg parser
        argparse._sys.argv = [  # pylint: disable=W0212
            "test", "foo_fun"]

        try:
            experiment.main(commands=[foo_fun])
        except RuntimeError:
            pass
        else:
            raise AssertionError("RuntimeError not raised")
        # Make sure logger is closed
        self.assertTrue(called[0])
        Logger.Logger.close = close_old


if __name__ == '__main__':
    unittest.main()
