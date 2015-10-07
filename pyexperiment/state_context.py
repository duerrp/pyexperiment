"""Provides contexts for states.

The substate_context allows using the state at a level below the first,
the

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import multiprocessing
import threading
from contextlib import contextmanager
import select

from pyexperiment.State import State


THREAD_LOCK = threading.Lock()
"""Lock protecting the state
"""


@contextmanager
def substate_context(substate_name):
    """Replaces global state with sub section of real state within the context
    """
    original_getitem = State.__getitem__
    original_setitem = State.__setitem__
    original_delitem = State.__delitem__
    original_iter = State.__iter__

    def getsubitem(self, key):
        """Get an item
        """
        if not key.startswith('__'):
            key = substate_name + State.SECTION_SEPARATOR + key
        State.__setitem__ = original_setitem
        try:
            value = original_getitem(self, key)
        except Exception as err:
            raise err
        finally:
            State.__setitem__ = setsubitem
        return value

    def setsubitem(self, key, value):
        """Set an item
        """
        if not key.startswith('__'):
            key = substate_name + State.SECTION_SEPARATOR + key
        original_setitem(self, key, value)

    def delsubitem(self, key):
        """Delete an item
        """
        if not key.startswith('__'):
            key = substate_name + State.SECTION_SEPARATOR + key
        original_delitem(self, key)

    def subiter(self):
        """Iterate
        """
        return original_getitem(self, substate_name).__iter__()

    State.__getitem__ = getsubitem
    State.__setitem__ = setsubitem
    State.__delitem__ = delsubitem
    State.__iter__ = subiter

    try:
        yield
    except Exception as err:
        raise err
    finally:
        State.__getitem__ = original_getitem
        State.__setitem__ = original_setitem
        State.__delitem__ = original_delitem
        State.__iter__ = original_iter


@contextmanager
def thread_state_context():
    """Locks the operations on the state for use in threads
    """
    original_getitem = State.__getitem__
    original_setitem = State.__setitem__
    original_delitem = State.__delitem__

    def save_getitem(self, key):
        """Get an item
        """
        with THREAD_LOCK:
            item = original_getitem(self, key)
        return item

    def save_setitem(self, key, value):
        """Set an item
        """
        with THREAD_LOCK:
            original_setitem(self, key, value)

    def save_delitem(self, key):
        """Delete an item
        """
        with THREAD_LOCK:
            try:
                State.__getitem__ = original_getitem
                State.__setitem__ = original_setitem
                State.__delitem__ = original_delitem
                original_delitem(self, key)
            except Exception as err:
                raise err
            finally:
                State.__getitem__ = save_getitem
                State.__setitem__ = save_setitem
                State.__delitem__ = save_delitem

    State.__getitem__ = save_getitem
    State.__setitem__ = save_setitem
    State.__delitem__ = save_delitem

    try:
        yield
    except Exception as err:
        raise err
    finally:
        State.__getitem__ = original_getitem
        State.__setitem__ = original_setitem
        State.__delitem__ = original_delitem


@contextmanager
def processing_state_context():
    """Locks the operations on the state for use with multiprocessing
    """
    get_pipe = multiprocessing.Pipe()
    set_pipe = multiprocessing.Pipe()
    del_pipe = multiprocessing.Pipe()
    thread_pipe = multiprocessing.Pipe()

    mp_lock = multiprocessing.Lock()

    with thread_state_context():
        orig_get_set_del = (State.__getitem__,
                            State.__setitem__,
                            State.__delitem__)

        def save_getitem(_self, key):
            """Get an item
            """
            with mp_lock:
                get_pipe[0].send(key)
                item, err = get_pipe[0].recv()
            if err is not None:
                raise err
            return item

        def save_setitem(_self, key, value):
            """Set an item
            """
            with mp_lock:
                set_pipe[0].send((key, value))
                err = set_pipe[0].recv()
            if err is not None:
                raise err

        def save_delitem(_self, key):
            """Delete an item
            """
            with mp_lock:
                del_pipe[0].send((key))
                err = del_pipe[0].recv()
            if err is not None:
                raise err

        def handler_thread():
            """Target for thread handling the state in the main process
            """
            def handle_get():
                """Handle getitem from process"""
                key = get_pipe[1].recv()
                try:
                    item = orig_get_set_del[0](State.get_instance(), key)
                except Exception as err:  # pylint: disable=broad-except
                    # Raise the exception inside the process
                    get_pipe[1].send((None, err))
                else:
                    get_pipe[1].send((item, None))

            def handle_set():
                """Handle setitem from process
                """
                key, value = set_pipe[1].recv()
                try:
                    orig_get_set_del[1](State.get_instance(), key, value)
                except Exception as err:  # pylint: disable=broad-except
                    # Raise the exception inside the process
                    set_pipe[1].send(err)
                    # raise err
                else:
                    set_pipe[1].send(None)

            def handle_del():
                """Handle delitem from process
                """
                key = del_pipe[1].recv()
                try:
                    State.__getitem__ = orig_get_set_del[0]
                    State.__setitem__ = orig_get_set_del[1]
                    State.__delitem__ = orig_get_set_del[2]
                    orig_get_set_del[2](State.get_instance(), key)
                except Exception as err:  # pylint: disable=broad-except
                    # Raise the exception inside the process
                    del_pipe[1].send(err)
                    # raise err
                else:
                    del_pipe[1].send(None)
                finally:
                    State.__getitem__ = save_getitem
                    State.__setitem__ = save_setitem
                    State.__delitem__ = save_delitem

            while True:
                ins, _out, _err = select.select([get_pipe[1],
                                                 set_pipe[1],
                                                 del_pipe[1],
                                                 thread_pipe[0]],
                                                [],
                                                [],
                                                None)

                if get_pipe[1] in ins:
                    handle_get()
                if set_pipe[1] in ins:
                    handle_set()
                if del_pipe[1] in ins:
                    handle_del()
                if thread_pipe[0] in ins:
                    if thread_pipe[0].recv():
                        break

        State.__getitem__ = save_getitem
        State.__setitem__ = save_setitem
        State.__delitem__ = save_delitem

        thread = threading.Thread(target=handler_thread)
        thread.start()

        try:
            yield
        except Exception as err:
            raise err
        finally:
            pipes = [set_pipe[1], get_pipe[1]]
            for pipe in pipes:
                pipe.close()
            thread_pipe[1].send(True)
            thread_pipe[1].close()
            thread.join()
            State.__getitem__ = orig_get_set_del[0]
            State.__setitem__ = orig_get_set_del[1]
            State.__delitem__ = orig_get_set_del[2]
