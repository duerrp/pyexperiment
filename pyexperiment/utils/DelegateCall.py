"""Provides a multiprocessing-safe way to aggregate results from
multiple function calls.

In multi-process programs, it is oft often useful to delegate a
function call - e.g., writing a log message to a file - to another
process to avoid conflicts. :class:`pyexperiment.utils.DelegateCall`
implements a functor that, when called, passes the argument data to a
function running in a thread of the process that created the
DelegateCall object. The callback itself must be thread-safe though.

Written by Peter Duerr

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys
import multiprocessing
import threading
import traceback


class DelegateCall(object):  # pylint: disable=too-few-public-methods
    """Helper class that provides a multiprocessing-safe way to aggregate
    results from multiple function calls.

    The arguments to the __call__ function are passed through a
    multiprocessing.Queue to the process where the class was
    initialized (i.e., all arguments must be serializable).

    """
    def __init__(self, callback):
        """Initializer, takes a callback that processes the received data in
        the original process.
        """
        # The callback
        self.callback = callback

        # The queue that aggregates the data
        self._queue = multiprocessing.JoinableQueue(-1)

        # The thread that processes it
        processor_thread = threading.Thread(target=self._receive)
        processor_thread.daemon = True
        processor_thread.start()

    def __call__(self, *data):
        """Send data, can be called from any process
        """
        self._queue.put_nowait(data)

    def join(self):
        """Returns true if there are currently no pending callbacks
        """
        return self._queue.join()

    def _receive(self):
        """Loops indefinitely receiving calls from the queue
        """
        while True:
            try:
                data = self._queue.get()
                self.callback(*data)
                self._queue.task_done()
            except EOFError:  # pragma: no cover
                # This is covered, but not reported
                break
            # This should really catch every other exception!
            except Exception:  # pylint: disable=broad-except
                traceback.print_exc(file=sys.stderr)
                # Should not get stuck here
                self._queue.task_done()
