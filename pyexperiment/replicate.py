"""Repliate allows running a target function multiple times.

The number of replicates is defined by a confguration value and replicate can
be run with or without multiprocessing.

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Comment to avoid pylint complaining about duplicate lines
import multiprocessing
import functools
import traceback
import threading

from pyexperiment.state_context import substate_context
from pyexperiment.state_context import processing_state_context
from pyexperiment import conf
from pyexperiment import state
from pyexperiment import log

# For python2.x compatibility
from six.moves import range  # pylint: disable=redefined-builtin, import-error

SUBSTATE_KEY_PATTERN = 'replicate%03d'
"""The pattern used to create the subsection of the state for replicates
"""


def _replicate_single_thread(function,
                             no_replicates,
                             subkey_pattern=SUBSTATE_KEY_PATTERN):
    """Replicate the experiment defined by the function
    """
    for i in range(no_replicates):
        with substate_context(subkey_pattern % i):
            log.debug("Running " + subkey_pattern % i)
            function()


class TargetCreator(object):  # pylint: disable=too-few-public-methods
    """Creates a target for a multiprocessed replicate
    """
    def __init__(self, target, ready_queue, context):
        self.target = target
        self.ready_queue = ready_queue
        self.context = context
        try:
            functools.update_wrapper(self, target)
        except AttributeError:
            pass

    def __call__(self):
        with substate_context(self.context):
            self.ready_queue.put(True)
            log.debug("Running " + self.context)
            try:
                result = self.target()
            except Exception as err:
                log.fatal("Error in sub-process: %s", traceback.format_exc())
                raise err
        return result


def _replicate_multiprocessing(function,
                               no_replicates,
                               no_processes,
                               subkey_pattern=SUBSTATE_KEY_PATTERN):
    """Replicate the experiment defined by the function in multiple processes
    """
    with processing_state_context():
        pool = multiprocessing.Pool(processes=no_processes)
        manager = multiprocessing.Manager()
        ready_queue = manager.Queue()  # pylint: disable=no-member
        result_threads = []
        for i in range(no_replicates):
            # Create a target function to be run in  a separate process
            # using a separate state context
            target = TargetCreator(function, ready_queue, subkey_pattern % i)
            result = pool.apply_async(target)
            # Use a thread to wait for the result
            waiter = threading.Thread(target=result.get)
            waiter.start()
            result_threads.append(waiter)
            # Make sure the process is really running (probably not necessary)
            while not ready_queue.get():
                pass  # pragma: no cover

        # Wait for the pool, then join it
        log.debug("Closing pool")
        pool.close()
        log.debug("Joining pool")
        pool.join()

        # Make sure all the results are in
        log.debug("Joining threads")
        for thread in result_threads:
            thread.join()


def replicate(function,
              no_replicates=None,
              subkey_pattern=SUBSTATE_KEY_PATTERN,
              parallel=False,
              no_processes=None):
    """Replicate the experiment defined by the function.

    The results of state[key] lookups / assignments are stored in sub-states
    under the subkey_pattern. If multiprocessing is true, run the replicates in
    a pool of processes.
    """
    no_replicates = no_replicates or int(conf['pyexperiment.n_replicates'])
    if not parallel:
        _replicate_single_thread(function, no_replicates, subkey_pattern)
    else:
        no_processes = no_processes or int(conf['pyexperiment.n_processes'])
        _replicate_multiprocessing(function,
                                   no_replicates=no_replicates,
                                   no_processes=no_processes,
                                   subkey_pattern=subkey_pattern)


def collect_results(key,
                    subkey_pattern=SUBSTATE_KEY_PATTERN,
                    no_replicates=None):
    """Collect the results of a replicated experiment in a list
    """
    result = []
    no_replicates = no_replicates or int(conf['pyexperiment.n_replicates'])
    for i in range(no_replicates):
        with substate_context(subkey_pattern % i):
            result.append(state[key])
    return result
