"""Framework for quick and clean experiments with python.

For a simple example to adapt to your own needs, check the example
file.

Written by Peter Duerr.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import sys
from datetime import datetime
import argparse
import subprocess
try:
    import argcomplete
    AUTO_COMPLETION = True
except ImportError:
    AUTO_COMPLETION = False
from contextlib import contextmanager
from inspect import getargspec
import multiprocessing

from pyexperiment import conf
from pyexperiment import log
from pyexperiment import state
from pyexperiment.State import StateHandler
from pyexperiment.utils.printers import print_bold  # pylint: disable=E0611

from pyexperiment.utils.interactive import embed_interactive

DEFAULT_CONFIG_SPECS = ("[pyexperiment]\n"
                        "verbosity = option('DEBUG','INFO','WARNING','ERROR',"
                        "'CRITICAL',default='WARNING')\n"
                        "log_to_file = boolean(default=False)\n"
                        "log_filename = string(default=log.txt)\n"
                        "log_file_verbosity = option('DEBUG','INFO','WARNING',"
                        "'ERROR','CRITICAL',default='DEBUG')\n"
                        "rotate_n_logs = integer(min=0, default=5)\n"
                        "print_timings = boolean(default=False)\n"
                        "load_state = boolean(default=False)\n"
                        "save_state = boolean(default=False)\n"
                        "state_filename = "
                        "string(default=experiment_state.h5f)\n"
                        "rotate_n_state_files = integer(min=0, default=5)\n"
                        "n_replicates = integer(min=1, default=25)\n"
                        "n_processes = integer(min=1, default={n_processes})\n"
                        "[[plot]]\n"
                        "font_size = integer(min=1, default=14)\n"
                        "label_size = integer(min=1, default=14)\n"
                        "use_tex = boolean(default=True)\n"
                        "line_width = integer(min=1, default=4)\n"
                        "[[[seaborn]]]\n"
                        "enable = boolean(default=True)\n"
                        "style = option('darkgrid','whitegrid','dark',"
                        "'white','ticks',default='darkgrid')\n"
                        "palette_name = string(default=colorblind)\n"
                        "desat = float(min=0.0, max=1.0, default=0.6)\n"
                        "".format(
                            n_processes=multiprocessing.cpu_count()))
"""Default specification for the experiment's configuration
"""

DEFAULT_CONFIG_FILENAME = "./config.ini"
"""Default name for the configuration file
"""

TESTS = []
"""List of all tests for the experiment. Filled by main.
"""

COMMANDS = []
"""List of all commands for the experiment. Filled by main.
"""


@contextmanager
def logging_context():
    """Initialize and close the logger based on the configuration
    """
    # Get options related to logging
    verbosity = conf['pyexperiment.verbosity']
    log_to_file = conf['pyexperiment.log_to_file']
    if (((isinstance(log_to_file, str) and log_to_file == 'True')
         or (isinstance(log_to_file, bool) and log_to_file))):
        log_filename = conf['pyexperiment.log_filename']
    else:
        log_filename = None
    log_file_verbosity = conf['pyexperiment.log_file_verbosity']
    rotate_n_logs = int(conf['pyexperiment.rotate_n_logs'])

    # Setup the logger for the configuration
    log.initialize(console_level=verbosity,
                   filename=log_filename,
                   file_level=log_file_verbosity,
                   no_backups=rotate_n_logs)

    # Give control back, but catch exceptions
    try:
        yield
    except Exception as err:
        # Reraise exception after the logger is closed
        raise err
    finally:
        log.close()


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
    conf.show()


def save_config(filename):
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
        state_file = conf['pyexperiment.state_filename']
    else:
        state_file = arguments[0]
    print_bold("Load state from file '%s'",
               state_file)
    try:
        state.load(state_file, lazy=False, raise_error=True)
    except IOError as err:
        print(err)
    else:
        if len(state) > 0:
            state.show()
        else:
            print("State empty")


def activate_autocompletion():
    """Activate auto completion for your experiment with zsh or bash.

    Call with eval \"$(script_name activate_autocompletion)\".
    In zsh you may need to call `autoload bashcompinit` and
    `bashcompinit` first.

    """
    process = subprocess.Popen(
        ["register-python-argcomplete", sys.argv[0].split("/")[-1]],
        stdout=subprocess.PIPE)
    out, _err = process.communicate()
    print(out)


def collect_commands(default, commands):
    """Add default commands
    """
    default_commands = [help,
                        test,
                        show_tests,
                        show_config,
                        save_config,
                        show_state]

    if default is not None and len(getargspec(default).args) > 0:
        raise TypeError("Main function cannot take arguments.")

    def show_commands():
        """Print the available commands
        """
        cmds = commands
        if default is not None and default not in cmds:
            cmds = [default] + commands
        print_bold("Available commands:")
        all_commands = cmds + default_commands + [show_commands]
        if AUTO_COMPLETION:
            all_commands += [activate_autocompletion]
        names = [command.__name__ for command in all_commands]
        for name in names:
            print("\t" + str(name))

    all_commands = commands + default_commands + [show_commands]
    if AUTO_COMPLETION:
        all_commands += [activate_autocompletion]

    return all_commands


def format_command_help(default, commands):
    """Format the docstrings of the commands.
    """
    string = ("available commands:\n\n" +
              "".join(["  "
                       + "%-22s" % (command.__name__
                                    + (' (default)'
                                       if command == default else '')
                                    + ':')
                       + "".join(command.__doc__.replace(
                           "\n    ", " ").split(".")[0])
                       + "\n"
                       for command in commands
                       if command.__doc__ is not None]))
    return string


def setup_arg_parser(default, commands, description):
    """Setup the argument parser for the experiment
    """
    command_help = format_command_help(default, commands)

    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog=(command_help))

    arg_parser.add_argument('command',
                            help=('choose a command to run'
                                  + (', running '
                                     + default.__name__
                                     + ' by default'
                                     if (default is not None
                                         and default in commands)
                                     else '')),
                            type=str,
                            choices=[command.__name__
                                     for command in commands],
                            nargs='?')

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

    arg_parser.add_argument(
        '-i',
        '--interactive',
        action='store_true',
        help='drop to interactive prompt after COMMAND')

    arg_parser.add_argument(
        '--verbosity',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        action='store',
        help="choose the console logger's verbosity")

    arg_parser.add_argument(
        '-v',
        action='store_true',
        help="shortcut for --verbosity DEBUG")

    arg_parser.add_argument(
        '-j', '--processes',
        nargs=1,
        type=int,
        action='store',
        help="set number of parallel processes used")

    arg_parser.add_argument(
        '--print-timings',
        action='store_true',
        help="print logged timings")

    if AUTO_COMPLETION:
        argcomplete.autocomplete(arg_parser)

    return arg_parser


def handle_shortcuts(args):
    """Handle argument shortcuts
    """
    # Handle verbosity
    if args.verbosity is not None:
        if args.option is None:
            args.option = []
        args.option.append(('pyexperiment.verbosity',
                            args.verbosity))
    elif args.v:
        if args.option is None:
            args.option = []
        args.option.append(('pyexperiment.verbosity',
                            'DEBUG'))
    # Handle --processes
    if args.processes:
        if args.option is None:
            args.option = []
        args.option.append(('pyexperiment.n_processes',
                            str(args.processes[0])))

    # Handle --print-timings
    if args.print_timings:
        if args.option is None:
            args.option = []
        args.option.append(('pyexperiment.print_timings',
                            'True'))


def configure(default, commands, config_specs, description):
    """Load configuration from command line arguments and optionally, a
    configuration file. Possible command line arguments depend on the
    list of supplied commands, the configuration depends on the
    supplied configuration specification.
    """
    arg_parser = setup_arg_parser(default, commands, description)
    args = arg_parser.parse_args()

    handle_shortcuts(args)

    conf.initialize(args.config,
                    [option.encode()
                     for option in config_specs.split('\n')],
                    args.option,
                    [option.encode()
                     for option in DEFAULT_CONFIG_SPECS.split('\n')])

    actual_command = default
    if args.command is not None:
        for command in commands:
            if command.__name__ == args.command:
                actual_command = command
                break
    else:
        if args.interactive:
            actual_command = lambda: None

    if actual_command is None:
        print("Error: Not enough arguments.")
        arg_parser.print_usage()
        return None, args.argument, args.interactive

    return actual_command, args.argument, args.interactive


def main(default=None,
         commands=None,
         config_spec="",
         tests=None,
         description=None):
    """Parses command line arguments and configuration, then runs the
    appropriate command.
    """
    start_time = datetime.now()
    log.debug("Start: '%s'", " ".join(sys.argv))
    log.debug("Time: '%s'", start_time)

    commands = collect_commands(default, commands or [])

    # Configure the application from the command line and get the
    # command to be run
    run_command, arguments, interactive = configure(
        default,
        commands,
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
    # and handle the state safely
    with logging_context(), \
        StateHandler(filename=conf['pyexperiment.state_filename'],
                     load=conf['pyexperiment.load_state'],
                     save=conf['pyexperiment.save_state'],
                     rotate_n_files=conf[
                         'pyexperiment.rotate_n_state_files']):

        # Run the command with the supplied arguments
        if run_command is not None:
            result = run_command(*arguments)

            if result is not None:
                print(result)

        # Drop to the interactive console if necessary, passing the result
        if interactive:
            embed_interactive(result=result)

        # After everything is done, print timings if necessary
        if (((isinstance(conf['pyexperiment.print_timings'], bool)
              and conf['pyexperiment.print_timings'])
             or conf['pyexperiment.print_timings'] == 'True')):
            log.print_timings()

        end_time = datetime.now()
        log.debug("End: '%s'", " ".join(sys.argv))
        log.debug("Time: '%s'", end_time)
        log.debug("Took: %.3fs", (end_time - start_time).total_seconds())
