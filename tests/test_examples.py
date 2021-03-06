"""Tests the examples for pyexperiment

The tests contained in this file verify the output generated by running
the example scripts with various command line arguments, thereby making
sure the command line interface works as expected.

When adding a new example, first make sure the output from the CLI is
correct. Then, by running this file directly, create files with the
expected output (for stdout and stderr respectively). Running the test
suite will then verify that the output matches the previously generated
files.

Note that to avoid problems with times and dates, any numbers appearing
in the output are not verified.

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import subprocess
import difflib
import os
import re
from toolz import thread_last


EXAMPLES = [
    ['./examples/minimal_cli'],
    ['./examples/minimal_cli', '-h'],
    ['./examples/minimal_cli', 'help'],
    ['./examples/minimal_cli', 'help', 'hello'],
    ['./examples/minimal_cli', 'help', 'world'],
    ['./examples/minimal_cli', 'help', 'test'],
    ['./examples/minimal_cli', 'help', 'show_tests'],
    ['./examples/minimal_cli', 'hello'],
    ['./examples/minimal_cli', 'world'],
    ['./examples/minimal_config'],
    ['./examples/minimal_config', '-h'],
    ['./examples/minimal_config', 'help'],
    ['./examples/minimal_config', 'help', 'simple'],
    ['./examples/minimal_config', 'help', 'nested'],
    ['./examples/minimal_config', 'help', 'test'],
    ['./examples/minimal_config', 'help', 'show_tests'],
    ['./examples/minimal_config', 'simple'],
    ['./examples/minimal_config', 'nested'],
    ['./examples/minimal_logging'],
    ['./examples/minimal_logging', '-h'],
    ['./examples/minimal_logging', 'help'],
    ['./examples/minimal_logging', 'help', 'run'],
    ['./examples/minimal_logging', 'help', 'timed'],
    ['./examples/minimal_logging', 'run'],
    ['./examples/minimal_logging', '--verbosity', 'DEBUG', 'run'],
    ['./examples/minimal_logging', '-v', 'run'],
    ['./examples/minimal_logging', '--verbosity', 'WARNING', 'run'],
    ['./examples/minimal_logging', '--verbosity', 'INFO', 'run'],
    ['./examples/minimal_logging', '--verbosity', 'ERROR', 'run'],
    ['./examples/minimal_logging', '--verbosity', 'CRITICAL', 'run'],
    ['./examples/minimal_logging', 'timed'],
    ['./examples/minimal_logging', '--verbosity', 'DEBUG', 'timed'],
    ['./examples/memoize', '-h'],
    ['./examples/memoize', '--help'],
    ['./examples/memoize', '--verbosity', 'DEBUG', '-o',
     'pyexperiment.save_state', 'False'],
    ['./examples/benchmarks', '-h'],
    ['./examples/benchmarks'],
    ]
"""The command line examples to be checked for matching stdout
"""


def format_example_name(example):
    """Formats an example command to a function or file name
    """
    return '_'.join(example).replace('-', '_').replace(
        '.', '_').replace('/examples/', '')[1:]


class TestExamples(unittest.TestCase):
    """Executes command line examples and checks the output
    """
    def check_shell(self, command, expected_stdout, expected_stderr):
        """Assert output of shell command is as expected
        """
        process = subprocess.Popen(command,
                                   universal_newlines=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        process.wait()
        stdout = invariant_output(process.stdout.read())
        stderr = invariant_output(process.stderr.read())
        stdout_diff = [dl for dl in (difflib.Differ().compare(
            stdout.splitlines(),
            expected_stdout.splitlines())) if not dl[0] == ' ']
        stderr_diff = [dl for dl in (difflib.Differ().compare(
            stderr.splitlines(),
            expected_stderr.splitlines())) if not dl[0] == ' ']
        self.assertEqual(remove_whitespace(str(stdout)),
                         remove_whitespace(str(expected_stdout)),
                         stdout_diff)
        self.assertEqual(remove_whitespace(str(stderr)),
                         remove_whitespace(str(expected_stderr)),
                         stderr_diff)


def add_tests():
    """Creates the tests and adds them to the ExampleTest
    """
    for example in EXAMPLES:
        def create_test(ex):
            """Create a test
            """
            def test(self):
                """Test the example
                """
                stdout_filename = ('./tests/example_outputs/' +
                                   format_example_name(ex)) + '.out'
                stderr_filename = ('./tests/example_outputs/' +
                                   format_example_name(ex)) + '.err'
                self.assertTrue(os.path.isfile(stdout_filename),
                                "Cannot find file with expected output "
                                "'%s'" % stdout_filename)
                with open(stdout_filename, 'r') as f_handle:
                    expected_stdout = f_handle.read()
                self.assertTrue(os.path.isfile(stderr_filename),
                                "Cannot find file with expected output "
                                "'%s'" % stderr_filename)
                with open(stdout_filename, 'r') as f_handle:
                    expected_stdout = f_handle.read()
                with open(stderr_filename, 'r') as f_handle:
                    expected_stderr = f_handle.read()
                self.check_shell(ex, expected_stdout, expected_stderr)

            return test

        setattr(TestExamples,
                'test_' + format_example_name(example),
                create_test(example))


def invariant_output(string):
    """Removes all changing elements from the string

    * Replaces all numbers in a string with the 'X' character
    * Removes all appearances of activate_autocompletion
    * Removes all newlines and whitespace from the string
    """
    numbers_regexp = r'\d'
    activate_autocomp_regexp = (r'((\n?[ ]*)|,)'
                                'activate_autocompletion'
                                '(:.*\n)?')
    return thread_last(string,
                       (re.sub, numbers_regexp, 'X'),
                       (re.sub, activate_autocomp_regexp, ''))


def remove_whitespace(string):
    """Removes spaces, tabs and newlines from the string
    """
    return thread_last(string,
                       (re.sub, r'\t*', ''),
                       (re.sub, r' *', ''),
                       (re.sub, r'\n*', ''))


def generate_expected():
    """Generates the expected results, be careful to double check the results
    """
    print("Generating expected output for examples, please check the results!")
    for ex in EXAMPLES:
        stdout_filename = ('./tests/example_outputs/' + format_example_name(ex)
                           + '.out')
        stderr_filename = ('./tests/example_outputs/' + format_example_name(ex)
                           + '.err')
        if ((not os.path.isfile(stdout_filename) or
             not os.path.isfile(stderr_filename))):
            print("Running: %s" % ex)
            process = subprocess.Popen(ex,
                                       universal_newlines=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            process.wait()
            stdout = invariant_output(process.stdout.read())
            stderr = invariant_output(process.stderr.read())
            with open(stdout_filename, 'w') as f_handle:
                f_handle.write(stdout)
            with open(stderr_filename, 'w') as f_handle:
                f_handle.write(stderr)

if __name__ == '__main__':
    generate_expected()
else:
    add_tests()
