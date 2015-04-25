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
from pyexperiment.utils.Singleton import InitializeableSingletonIndirector
from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalOrderedDict
from pyexperiment.Logger import TimingLogger

log = InitializeableSingletonIndirector(  # pylint: disable=invalid-name
    TimingLogger)
"""Pyexperiment's logger, re-wrapped here to avoid cyclical dependency
"""


class State(Singleton, HierarchicalOrderedDict):
    """Represents persistent state of an experiment
    """
    def __init__(self):
        """Initializer
        """
        super(State, self).__init__()

        # Keeps track of changed files
        self.changed = []
        self.lazy_load_filename = None

    def __getitem__(self, key):
        """Get the state with specified key
        """
        try:
            return super(State, self).__getitem__(key)
        except KeyError:
            if self.lazy_load_filename is not None:
                # Try to get the section from file
                with h5py.File(self.lazy_load_filename, "r") as h5file:
                    h5name = "state/" + "/".join(key.split("."))
                    value = pickle.loads(h5file[h5name].value)
                    self.__setitem__(key, value)
                    return value
            else:
                raise

    def __setitem__(self, key, value):
        """Stores state with key and value
        """
        super(State, self).__setitem__(key, value)
        self.changed.append(key)

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
        if self.base is None or len(self.base.keys()) == 0:
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
            log.debug("State does not need saving")
            return
        self.do_rollover(filename, rotate_n_state_files)
        log.debug("Saving state to file: '%s'", filename)
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

                save_level_to_group(self.base, state_grp)

        except IOError as err:
            raise IOError("Cannot save state to file '%s', (err: '%s')",
                          filename,
                          err)

    def load(self, filename, lazy=True):
        """Loads state from a h5f file
        """
        # Reset state
        self.base = OrderedDict()
        self.changed = []

        if lazy:
            # Load the data later when it's needed
            self.lazy_load_filename = filename
        else:
            self.lazy_load_filename = None

            try:
                with h5py.File(filename, 'r') as h5file:
                    log.info("Loading state from file '%s'", filename)

                    def load(group, level):
                        """Loads a whole h5 file as an Ordered dict
                        """
                        for key, value in group.items():
                            # TODO: Check if there is a better way
                            if isinstance(value, h5py._hl.group.Group):
                                if key not in level:
                                    level[key] = OrderedDict()
                                load(value, level[key])
                            else:
                                level[key] = pickle.loads(value.value)
                    load(h5file['state'], self.base)

            except IOError as err:
                raise IOError("Cannot load state from file '%s', (err: '%s')" %
                              (filename, err))

    def show(self):
        """Shows the state"""
        print(self)
        print("Hello", self.lazy_load_filename)
        # Force loading
        if self.lazy_load_filename is not None:
            self.load(self.lazy_load_filename, lazy=False)
        super(State, self).show()
