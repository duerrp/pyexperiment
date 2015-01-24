"""Provides helper class for multiprocessing-safe logging
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys
import multiprocessing
import threading
import traceback


class DelegateCall(object):
    """Helper class that provides a multiprocessing-safe way to aggregate
    results from multiple processes. The arguments to the __call__
    function are passed through a multiprocessing.Queue to the process
    where the class was initialized (i.e., all arguments must be
    serializable).
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

    def __call__(self, data):
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
                self.callback(data)
                self._queue.task_done()
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)
            finally:
                pass
