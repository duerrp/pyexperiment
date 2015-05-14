"""Provides printing in color

Written by Peter Duerr, inspired by a stackoverflow comment by airmind
(http://stackoverflow.com/a/384125/2481888).
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import


RESET_SEQ = "\033[0m"
"""Sequence used to reset console formatting
"""

COLOR_SEQ = "\033[1;%dm"
"""Sequence used to set color for console formatting
"""

# Foreground colors defined as 30 + index, bold
COLORS = {
    'black': COLOR_SEQ % 30,
    'red': COLOR_SEQ % 31,
    'green': COLOR_SEQ % 32,
    'yellow': COLOR_SEQ % 33,
    'blue': COLOR_SEQ % 34,
    'magenta': COLOR_SEQ % 35,
    'cyan': COLOR_SEQ % 36,
    'white': COLOR_SEQ % 37,
    'bold': "\033[1m"
    }


def colorize(string, color_s):
    """Colorize a string
    """
    # pylint:disable=no-value-for-parameter, assignment-from-no-return
    return color_s + string + RESET_SEQ


def _print_color(color, string, *args):
    """Prints string in color to stdout
    """
    print(colorize(string % args, color))


for color_name, color_seq in COLORS.items():
    def create_printer(color):
        """Creates the printer for the corresponding color
        """
        return lambda string, *args: _print_color(color, string, *args)

    vars()['print_' + color_name] = create_printer(color_seq)


def print_examples(message=None, *args):
    """Print an example message with every available printer
    """
    if message is None:
        message = "string: '%s', int: '%d', float: '%f'"
        args = ("foo".encode(), 123, 2.71)

    for name, printer in ((name, fun) for name, fun in globals().items()
                          if ((name.startswith('print_')
                               and not name == 'print_examples'
                               and callable(fun)))):
        print('%s("%s", %s)' % (
            name,
            message, ",".join((repr(arg) for arg in args))))
        printer("\t" + message + "\n", *args)
