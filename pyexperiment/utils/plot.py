"""Provides setup for matplotlib figures

Written by Peter Duerr.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import matplotlib
from matplotlib import pyplot as plt


def setup_matplotlib(font_size=14,
                     label_size=14,
                     use_tex=True,
                     linewidth=2):
    """Setup basic style for matplotlib figures
    """
    font_size = int(font_size)
    font = {'family': 'normal',
            'weight': 'normal',
            'size': font_size}
    # ** is elegant here
    matplotlib.rc('font', **font)  # pylint:disable=W0142

    matplotlib.rc('text', usetex=use_tex)
    matplotlib.rc('lines', linewidth=linewidth)

    label_size = int(label_size)
    matplotlib.rc('xtick', labelsize=label_size)
    matplotlib.rc('ytick', labelsize=label_size)


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


def setup_figure(name):
    """Setup a figure that can be closed by pressing 'q' and saved by
    pressing 's'.
    """
    fig = plt.figure()
    fig.canvas.set_window_title(name)
    quit_figure_on_key('q', fig)
