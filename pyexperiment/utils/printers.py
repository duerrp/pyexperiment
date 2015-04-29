"""Provides printing in color

Written by Peter Duerr, inspired by a stackoverflow comment by airmind
(http://stackoverflow.com/a/384125/2481888).
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from functools import partial


RESET_SEQ = "\033[0m"
"""Sequence used to reset console formatting
"""  # pylint:disable=W0105

COLOR_SEQ = "\033[1;%dm"
"""Sequence used to set color for console formatting
"""  # pylint:disable=W0105

BOLD_SEQ = "\033[1m"
"""Sequence used to set bold for console formatting
"""  # pylint:disable=W0105

# Foreground colors defined as 30 + index
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37


def wrap_seq(string, seq, reset=RESET_SEQ):
    """Wraps string in special sequence
    """
    return seq + string + reset


def colorize(string, color):
    """Colorize a string
    """
    return wrap_seq(string, COLOR_SEQ % color)


def print_color(color, string, *args):
    """Prints string in color to stdout
    """
    print(colorize(string % args, color))


def print_bold(msg, *args):
    """Prints message in bold to stdout
    """
    print(wrap_seq(msg % args, BOLD_SEQ))

# pylint:disable=C0103
print_black = partial(print_color, BLACK)
"""Prints message in black to stdout
"""  # pylint:disable=W0105

print_red = partial(print_color, RED)

"""Prints message in red to stdout
"""  # pylint:disable=W0105
print_green = partial(print_color, GREEN)
# pylint:disable=C0103
"""Prints message in green to stdout
"""  # pylint:disable=W0105
print_yellow = partial(print_color, YELLOW)
# pylint:disable=C0103
"""Prints message in yellow to stdout
"""  # pylint:disable=W0105
print_blue = partial(print_color, BLUE)
# pylint:disable=C0103
"""Prints message in blue to stdout
"""  # pylint:disable=W0105
print_magenta = partial(print_color, MAGENTA)
# pylint:disable=C0103
"""Prints message in magenta to stdout
"""  # pylint:disable=W0105
print_cyan = partial(print_color, CYAN)
# pylint:disable=C0103
"""Prints message in cyan to stdout
"""  # pylint:disable=W0105
print_white = partial(print_color, WHITE)
# pylint:disable=C0103
"""Prints message in white to stdout
"""  # pylint:disable=W0105
