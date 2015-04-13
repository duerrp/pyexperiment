"""Framework for quick and clean experiments with python.

For a simple example to adapt to your own needs, check the example
file.

Written by Peter Duerr.
"""

from __future__ import print_function
# from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import sys
from datetime import datetime
import argparse

from pyexperiment.conf import conf
from pyexperiment.log import log
from pyexperiment.state import state
from pyexperiment.utils.printers import print_bold

DEFAULT_CONFIG_SPECS = ("[basic]\n"
                        "verbosity = option('DEBUG','INFO','WARNING','ERROR',"
                        "'CRITICAL',default='WARNING')\n"
                        "log_to_file = boolean(default=False)\n"
                        "log_filename = string(default=log.txt)\n"
                        "log_file_verbosity = option('DEBUG','INFO','WARNING',"
                        "'ERROR','CRITICAL',default='DEBUG')\n"
                        "rotate_n_logs = integer(min=0, default=5)\n"
                        "print_timings = boolean(default=False)\n"
                        "save_state = "
                        "boolean(default=False)\n"
                        "state_filename = "
                        "string(default=experiment_state.h5f)\n"
                        "rotate_n_state_files = "
                        "integer(min=0, default=5)\n")
"""Default specification for the experiment's configuration
"""  # pylint:disable=W0105

DEFAULT_CONFIG_FILENAME = "./config.ini"
"""Default name for the configuration file
"""  # pylint:disable=W0105

TESTS = []
"""List of all tests for the experiment. Filled by main.
"""  # pylint:disable=W0105

COMMANDS = []
"""List of all commands for the experiment. Filled by main.
"""  # pylint:disable=W0105


def init_log():
    """Initialize the logger based on the configuration
    """
    # Get options related to logging
    verbosity = conf.get_value('basic.verbosity')
    log_to_file = conf.get_value('basic.log_to_file')
    if (((type(log_to_file) == str and log_to_file == 'True')
         or (type(log_to_file) == bool and log_to_file))):
        log_filename = conf.get_value('basic.log_filename')
    else:
        log_filename = None
    log_file_verbosity = conf.get_value('basic.log_file_verbosity')
    rotate_n_logs = int(conf.get_value('basic.rotate_n_logs'))

    # Setup the logger for the configuration
    log.init_main(console_level=verbosity,
                  filename=log_filename,
                  file_level=log_file_verbosity,
                  no_backups=rotate_n_logs)


# Redefining help should be ok here
def help(*args):  # pylint:disable=W0622
    """Shows help for a specified command.
    """
    help_dict = dict([(command.__name__,
                       command.__doc__) for command in COMMANDS])
    if len(args) == 0:
        print("To get help on a command, use %s help COMMAND" %
              sys.argv[0].replace("./", ""))
    else:
        if args[0] in help_dict.keys():
            print(help_dict[args[0]])
        else:
            print("Command '%s' not available." % args[0])


def show_config():
    """Print the configuration
    """
    conf.pretty_print()


def save_config(filename=None):
    """Save a configuration file to a filename
    """
    conf.save(filename)
    print("Wrote configuration to '%s'" % filename)


def test(*args):
    """Run tests for the experiment
    """
    all_tests = []
    for test_case in TESTS:
        if ((args == () or
             test_case.__name__ in args)):
            all_tests.append(
                unittest.TestLoader().loadTestsFromTestCase(test_case))

    suite = unittest.TestSuite(all_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)


def show_tests(*args):
    """Show available tests for the experiment
    """
    if TESTS == []:
        print_bold("No tests available")
    else:
        print_bold("Available tests:")
        for test_case in TESTS:
            if ((args == () or
                 test_case.__name__ in args)):
                print("\t"
                      + str(test_case.__name__)
                      + ":\t"
                      + test_case.__doc__.replace(
                          "\n", "").replace("    ", " "))


def show_state(*arguments):
    """Shows the contents of the state loaded by the configuration or from
    the file specified as an argument.
    """
    if len(arguments) == 0:
        state_file = conf.get_value('basic.state_filename')
    else:
        state_file = arguments[0]
    print_bold("Load state from file %s",
               state_file)
    state.load(state_file, lazy=False)
    state.show()


def collect_commands(commands):
    """Add default commands
    """
    default_commands = [help,
                        test,
                        show_tests,
                        show_config,
                        save_config,
                        show_state]

    def show_commands():
        """Print the possible commands for the experiments
        """
        print_bold("Available commands:")
        all_commands = commands + default_commands + [show_commands]
        names = [command.__name__ for command in all_commands]
        for name in names:
            print("\t" + str(name))

    all_commands = commands + default_commands + [show_commands]
    return all_commands


def format_command_help(commands):
    """Format the docstrings of the commands.
    """
    string = ("possible commands:\n\n" +
              "".join(["  "
                       + "%-22s" % (command.__name__ + ':')
                       + "".join(command.__doc__.replace(
                           "\n    ", " ").split(".")[0])
                       + "\n"
                       for command in commands]))
    return string


def configure(commands, config_specs, description):
    """Load configuration from command line arguments and optionally, a
    configuration file. Possible command line arguments depend on the
    list of supplied commands, the configuration depends on the
    supplied configuration specification.
    """
    command_help = format_command_help(commands)

    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog=(command_help))

    arg_parser.add_argument('command',
                            help='choose a command to run',
                            type=str,
                            choices=[command.__name__
                                     for command in commands],
                            nargs=1)

    arg_parser.add_argument('argument',
                            help='argument to the command',
                            type=str,
                            nargs='*')

    arg_parser.add_argument(
        '-c',
        '--config',
        help='specify a configuration file',
        type=str,
        default=DEFAULT_CONFIG_FILENAME)

    arg_parser.add_argument(
        '-o',
        '--option',
        help='override a configuration option',
        type=str,
        nargs=2,
        metavar=('key', 'value'),
        action='append')

    args = arg_parser.parse_args()

    conf.load(args.config,
              config_specs.split('\n'),
              args.option,
              DEFAULT_CONFIG_SPECS.split('\n'))

    for command in commands:
        if command.__name__ == args.command[0]:
            actual_command = command
            break

    return actual_command, args.argument


def main(commands=[],
         config_spec="",
         tests=None,
         description=None):
    """Parses command line arguments and configuration, then runs the
    appropriate command.
    """
    log.debug("Start: '%s'", " ".join(sys.argv))
    log.debug("Time: '%s'", datetime.now())

    commands = collect_commands(commands)

    # Configure the application from the command line and get the
    # command to be run
    run_command, arguments = configure(commands,
                                       config_spec,
                                       "Thanks for using %(prog)s."
                                       if description is None else description)

    # Store the commands and tests globally
    # I believe global is justified here for simplicity
    if tests is not None:
        global TESTS   # pylint:disable=W0603
        TESTS = tests
    global COMMANDS   # pylint:disable=W0603
    COMMANDS = commands

    # Initialize the main logger based on the configuration
    init_log()

    # Run the command with the supplied arguments
    # *arguments should be totally clear here
    run_command(*arguments)  # pylint:disable=W0142

    # If necessary, save the state
    if conf.get_value('basic.save_state'):
        state.save(conf.get_value('basic.state_filename'),
                   int(conf.get_value('basic.rotate_n_state_files')))

    # After everything is done, print timings if necessary
    if (((type(conf.get_value('basic.print_timings')) == bool
          and conf.get_value('basic.print_timings'))
         or conf.get_value('basic.print_timings') == 'True')):
        log.print_timings()
    else:
        log.close()
