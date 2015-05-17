"""Provides setup utilities for matplotlib figures.

The `setup_matplotlib` function will configure matplotlib's font size,
line width, etc. Calls after the first call are ignored unless the
override flag is set to True. The `setup_figure` function will call
`setup_matplotlib` without overriding an existing setup, and then return
the handle to a new figure, pre-configured with the 'q' key bound to
close the figure.

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


class AsyncPlot(object):
    """Plot asynchronously in a different process
    """
    @staticmethod
    def plot_process(queue, name):
        """Grabs data from the queue and plots it in a named figure
        """
        # Set up the figure and display it
        fig = setup_figure(name)
        plt.show(block=False)

        while True:
            # Get all the data currently on the queue
            data = []
            while not queue.empty():
                data.append(queue.get())

            # Check if poison pill (None) arrived or the figure was closed
            if None in data or not plt.fignum_exists(fig.number):
                # If yes, leave the process
                break
            else:
                # Plot the data, then wait 15ms for the plot to update
                for datum in data:
                    plt.plot(*datum)
                plt.pause(0.015)

    def __init__(self, name='pyexperiment'):
        """Initializer
        """
        self.queue = Queue()
        self.process = Process(target=self.plot_process,
                               args=(self.queue, name))
        self.process.start()

    def plot(self, *data):
        """Plots the data in the separate process
        """
        self.queue.put(data)

    def close(self):
        """Close the figure, join the process
        """
        self.queue.put(None)
        self.process.join()
