"""Provides setup utilities for matplotlib figures.

The `setup_plotting` function will configure basic plot options,
such as font size, line width, etc. Calls after the first call are
ignored unless the override flag is set to True. The `setup_figure`
function will call `setup_plotting` without overriding an existing
setup, and then return the handle to a new figure, pre-configured with
the 'q' key bound to close the figure.

The `AsyncPlot` class provides a simple way to plot some datapoints in
a separate process without blocking the execution of the main program.
Just create an `AsyncPlot` object and use the `plot` method. By
default, the window created by the `AsyncPlot` will stay open until
you close it. To close the window programatically, call the `close`
method on the `AsyncPlot` object.

Written by Peter Duerr.

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import matplotlib
from matplotlib import pyplot as plt

from multiprocessing import Process, Queue

from pyexperiment import conf
from pyexperiment import log

_SETUP_DONE = False
"""Flag indicating that matplotlib has already been set up
"""


def setup_plotting(options=None,
                   override_setup=True):
    """Setup basic style for matplotlib figures
    """
    if options is None:
        options = {}

    def option_or_conf(key, default):
        """Get a value from a dictionary, the configuration or a default value
        """
        prefix = 'pyexperiment.plot'
        if key in options:
            return options[key]
        elif prefix + conf.SECTION_SEPARATOR + key in conf:
            return conf[prefix + conf.SECTION_SEPARATOR + key]
        else:
            return default

    # Import seaborn if required
    sns = None
    if option_or_conf('seaborn.enable', True):
        try:
            import seaborn as sns
        except ImportError:
            log.warning("Cannot import seaborn. Proceeding without.")

    # Global should be ok here
    global _SETUP_DONE  # pylint: disable=global-statement
    if not override_setup and _SETUP_DONE:
        return False

    font_size = int(option_or_conf('font_size', 14))
    font = {'family': 'normal',
            'weight': 'normal',
            'size': font_size}

    matplotlib.rc('font', **font)

    matplotlib.rc('text', usetex=bool(option_or_conf('use_tex', True)))
    matplotlib.rc('lines', linewidth=int(option_or_conf('line_width', 4)))
    matplotlib.rc('figure', facecolor='white')

    label_size = int(option_or_conf('label_size', 14))
    matplotlib.rc('xtick', labelsize=label_size)
    matplotlib.rc('ytick', labelsize=label_size)

    if sns is not None:
        sns.set_style(option_or_conf('seaborn.style', 'darkgrid'))
        sns.set_palette(option_or_conf('seaborn.palette_name',
                                       'colorblind'),
                        desat=option_or_conf('seaborn.desat', 0.6))

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


def setup_figure(name='pyexperiment', figsize=None):
    """Setup a figure that can be closed by pressing 'q' and saved by
    pressing 's'.
    """
    setup_plotting(override_setup=False)

    fig = plt.figure(figsize=figsize)
    fig.canvas.set_window_title(name)
    quit_figure_on_key('q', fig)
    return fig


class AsyncPlot(object):
    """Plot asynchronously in a different process
    """
    @staticmethod
    def plot_process(queue,
                     name,
                     labels=None,
                     x_scale='linear',
                     y_scale='linear'):
        """Grabs data from the queue and plots it in a named figure
        """
        # Set up the figure and display it
        fig = setup_figure(name)
        plt.show(block=False)
        if labels is not None:
            plt.xlabel(labels[0])
            plt.ylabel(labels[1])
        plt.xscale(x_scale)
        plt.yscale(y_scale)

        while True:
            # Get all the data currently on the queue
            data = []
            while not queue.empty():
                data.append(queue.get())

            # If there is no data, no need to plot, instead wait for a
            # while
            if len(data) == 0 and plt.fignum_exists(fig.number):
                plt.pause(0.015)
                continue

            # Check if poison pill (None) arrived or the figure was closed
            if None in data or not plt.fignum_exists(fig.number):
                # If yes, close the figure and leave the process
                plt.close(fig)
                break
            else:
                # Plot the data, then wait 15ms for the plot to update
                for datum in data:
                    plt.plot(*datum[0], **datum[1])
                plt.pause(0.015)

    def __init__(self,
                 name='pyexperiment',
                 labels=None,
                 x_scale='linear',
                 y_scale='linear'):
        """Initializer
        """
        self.queue = Queue()
        self.process = Process(target=self.plot_process,
                               args=(self.queue,
                                     name,
                                     labels,
                                     x_scale,
                                     y_scale))
        self.process.start()

    def plot(self, *args, **kwargs):
        """Plots the data in the separate process
        """
        if self.process.is_alive():
            self.queue.put((args, kwargs))

    def close(self):
        """Close the figure, join the process
        """
        self.queue.put(None)
        self.process.join()
