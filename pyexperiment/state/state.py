"""Handles persistent state for an experiment, allowing to save and
restore from disk easily.

Python objects in general are stored in a dictionary that can be
accessed with set_state and get_state. State can be stored to disk and
reloaded with save_state and load_state respectively.

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

if True:  # Ugly, but makes pylint happy
    # pylint:disable=import-error
    from six.moves import cPickle as pickle
    from six.moves import range  # pylint: disable=redefined-builtin

import numpy as np
import h5py
import os
import shutil
from collections import OrderedDict

from pyexperiment.utils.Singleton import Singleton
from pyexperiment.log import log
from pyexperiment.utils.printers import print_bold


class State(Singleton):
    """Represents persistent state of an experiment
    """
    def __init__(self):
        """Initializer
        """
        # The dictionary representing the state
        self.state = OrderedDict()

        # Keeps track of changed files
        self.changed = []
        self.lazy_load_filename = None

    def get_state(self, name):
        """Get the state with specified name
        """
        if self.state is None:
            raise AttributeError("State not initialized yet")
        else:
            split_name = name.split(".")
            level = 0
            section = self.state
            while level < len(split_name) - 1:
                try:
                    section = section[split_name[level]]
                    level += 1
                except KeyError as err:
                    if self.lazy_load_filename is not None:
                        # Try to get the section from file
                        with h5py.File(self.lazy_load_filename, "r") as h5file:
                            h5name = "state/" + "/".join(name.split("."))
                            return pickle.loads(h5file[h5name].value)

                    raise KeyError(
                        "State does not contain section '%s', (err: '%s')",
                        ".".join(level[0:level]),
                        err
                    )
            try:
                value = section[split_name[level]]
                return value
            except KeyError as err:
                if self.lazy_load_filename is not None:
                    # Try to get the section from file
                    with h5py.File(self.lazy_load_filename, "r") as h5file:
                        h5name = "state/" + "/".join(name.split("."))
                        return pickle.loads(h5file[h5name].value)

                raise KeyError(
                    "State does not contain value '%s', (err: '%s')",
                    name,
                    err
                )

    def set_state(self, name, value):
        """Stores state with name and value
        """
        if self.state is None:
            raise AttributeError("state not initialized yet")
        else:
            split_name = name.split(".")
            level = 0
            section = self.state
            while level < len(split_name) - 1:
                if split_name[level] not in section:
                    section[split_name[level]] = OrderedDict()
                section = section[split_name[level]]
                level += 1
            try:
                section[split_name[level]] = value
            except TypeError as err:
                print("Cannot assign to state(%s), not section (%s)" %
                      (".".join(split_name[:level]), err))
            self.changed.append(name)

    def do_rollover(self, filename, rotate_n_state_files=0):
        """Rotate state files (as in logging module). Preserves the content of
        files with lazy_loading.
        """
        if rotate_n_state_files > 0:
            for i in range(rotate_n_state_files - 1, 0, -1):
                sfn = "%s.%d" % (filename, i)
                dfn = "%s.%d" % (filename, i + 1)
                if os.path.exists(sfn):
                    # print("%s -> %s" % (sfn, dfn))
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = filename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            if os.path.exists(filename):
                if self.lazy_load_filename is None:
                    os.rename(filename, dfn)
                else:
                    if self.lazy_load_filename == filename:
                        shutil.copyfile(filename, dfn)
                    else:
                        os.rename(filename, dfn)
                        shutil.copyfile(self.lazy_load_filename, filename)

    def need_saving(self):
        """Checks if state needs to be saved
        """
        if self.state is None or len(self.state.keys()) == 0:
            log.debug("No need to save empty state...")
            return False
        if not self.changed:
            log.debug("No need to save unchanged state...")
            return False

        # Otherwise
        return True

    def save(self, filename, rotate_n_state_files=0):
        """Saves state to a h5f file, rotating if necessary
        """
        if not self.need_saving():
            return
        self.do_rollover(filename, rotate_n_state_files)
        try:
            # Open data file and create groups
            with h5py.File(filename, 'a') as h5file:
                state_grp = h5file.require_group("state")
                # Save the state

                def save_level_to_group(level, group):
                    """Saves a state dict level to a h5 group
                    """
                    for key, value in level.items():
                        if isinstance(value, OrderedDict):
                            # Go to next level
                            next_group = group.require_group(key)
                            save_level_to_group(value, next_group)
                        else:
                            # Check if we need to delete
                            if key in group:
                                del group[key]

                            # Pickle and save
                            pickled_state = pickle.dumps(value)
                            pickled_state_array = np.array(pickled_state)
                            h5file.create_dataset(
                                group.name + "/" + key,
                                data=pickled_state_array)

                save_level_to_group(self.state, state_grp)

        except IOError as err:
            raise IOError("Cannot save state to file '%s', (err: '%s')",
                          filename,
                          err)

    def load(self, filename, lazy=True):
        """Loads state from a h5f file
        """
        # Reset state
        self.state = OrderedDict()
        self.changed = []

        if lazy:
            # Load the data later when it's needed
            self.lazy_load_filename = filename
            return
        try:
            with h5py.File(filename, 'r') as h5file:
                log.info("Loading state from file '%s'", filename)

                def load(group, level):
                    """Loads a whole h5 file as an Ordered dict
                    """
                    for key, value in group.items():
                        if isinstance(value, h5py._hl.group.Group):
                            if key not in level:
                                level[key] = OrderedDict()
                            load(value, level[key])
                        else:
                            level[key] = pickle.loads(value.value)
                load(h5file['state'], self.state)

        except IOError as err:
            raise IOError("Cannot load state from file '%s', (err: '%s')" %
                          (filename, err))
        self.changed = []

    def show(self):
        """Prints the content of the state
        """
        def show_level(level, prefix):
            """Saves a state dict level to a h5 group
            """
            for key, value in level.items():
                if isinstance(value, OrderedDict):
                    # Go to next level
                    print(prefix + "[" + key + "]")
                    show_level(level[key], prefix + "  ")
                else:
                    print(prefix + str(key) + ":" + repr(value))

        print_bold("Current state:")
        show_level(self.state, " ")


# Provide easy access to the singleton state at module level
get_state = State.get_instance().get_state
set_state = State.get_instance().set_state
save = State.get_instance().save
load = State.get_instance().load
show = State.get_instance().show

if __name__ == '__main__':
    # Test writing some data
    data = [1, 2, 3, 4]
    set_state('list', data)

    save('test.h5f')
    set_state('list', [1, 2])
    data2 = get_state('list')

    load('test.h5f')
    data3 = get_state('list')

    assert data != data2
    assert data == data3
