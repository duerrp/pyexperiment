"""Provides setup utilities for matplotlib figures.

The `setup_matplotlib` function will configure matplotlib's font size,
line width, etc. Calls after the first call are ignored unless the
override flag is set to True. The `setup_figure` function will call
`setup_matplotlib` without overriding an existing setup, and then return
the handle to a new figure, pre-configured with the 'q' key bound to
close the figure.

Written by Peter Duerr.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import matplotlib
from matplotlib import pyplot as plt


_SETUP_DONE = False
"""Flag indicating that matplotlib has already been set up
"""


def setup_matplotlib(font_size=14,
                     label_size=14,
                     use_tex=True,
                     linewidth=2,
                     override_setup=True):
    """Setup basic style for matplotlib figures
    """
    # Global should be ok here
    global _SETUP_DONE  # pylint: disable=global-statement
    if not override_setup and _SETUP_DONE:
        return False

    font_size = int(font_size)
    font = {'family': 'normal',
            'weight': 'normal',
            'size': font_size}

    matplotlib.rc('font', **font)

    matplotlib.rc('text', usetex=use_tex)
    matplotlib.rc('lines', linewidth=linewidth)

    label_size = int(label_size)
    matplotlib.rc('xtick', labelsize=label_size)
    matplotlib.rc('ytick', labelsize=label_size)

    _SETUP_DONE = True
    return True


def quit_figure_on_key(key, figure=None):
    """Add handler to figure (defaults to current figure) that closes it
    on a key press event.
    """

    def quit_on_keypress(event):
        """Quit the figure on key press
        """
        if event.key == key:
            plt.close(event.canvas.figure)

    if figure is None:
        figure = plt.gcf()
    figure.canvas.mpl_connect('key_press_event', quit_on_keypress)


def setup_figure(name='pyexperiment'):
    """Setup a figure that can be closed by pressing 'q' and saved by
    pressing 's'.
    """
    setup_matplotlib(override_setup=False)

    fig = plt.figure()
    fig.canvas.set_window_title(name)
    quit_figure_on_key('q', fig)
    return fig
