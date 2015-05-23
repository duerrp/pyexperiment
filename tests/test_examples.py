"""Tests the examples for pyexperiment

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
    ]


def format_example_name(example):
    """Formats an example command to a function or file name
    """
    return '_'.join(example).replace('-', '_').replace(
        '.', '_').replace('/examples/', '')[1:]


class TestExamples(unittest.TestCase):
    """Base class for command line tests
    """
    def check_shell(self, command, expected_output):
        """Assert output of shell command is as expected
        """
        output = subprocess.check_output(command, universal_newlines=True)
        diff = [dl for dl in (difflib.Differ().compare(
            output.splitlines(),
            expected_output.splitlines())) if not dl[0] == ' ']
        self.assertEqual(str(output),
                         str(expected_output),
                         diff)


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
                filename = ('./tests/example_outputs/' +
                            format_example_name(ex))
                self.assertTrue(os.path.isfile(filename),
                                "Cannot find file with expected output "
                                "'%s'" % filename)
                with open(filename, 'r') as f_handle:
                    expected = f_handle.read()
                self.check_shell(ex, expected)

            return test

        setattr(TestExamples,
                'test_' + format_example_name(example),
                create_test(example))


def generate_expected():
    """Generates the expected results, be careful to double check the results
    """
    print("Generating expected output for examples, please check the results!")
    for ex in EXAMPLES:
        filename = './tests/example_outputs/' + format_example_name(ex)
        if not os.path.isfile(filename):
            print("Running: %s" % ex)
            output = subprocess.check_output(ex, universal_newlines=True)
            print(output)
            with open(filename, 'w') as f_handle:
                f_handle.write(output)

if __name__ == '__main__':
    generate_expected()
else:
    add_tests()
