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


class _Deleted(object):  # pylint: disable=too-few-public-methods
    """Sentinel for deleted state values
    """
    def __repr__(self):
        """Represent deleted values"""
        return 'deleted state'
DELETED = _Deleted()
del _Deleted


class _Unloaded(object):  # pylint: disable=too-few-public-methods
    """Sentinel for values that have to be loaded first
    """
    def __repr__(self):
        """Represent unloaded values"""
        return 'state not loaded yet'
UNLOADED = _Unloaded()
del _Unloaded


class State(Singleton,  # pylint: disable=too-many-ancestors
            HierarchicalOrderedDict):
    """Represents persistent state of an experiment.
    """
    def __init__(self, filename=None):
        """Initializer
        """
        super(State, self).__init__()

        # Keep track of changed values
        self.changed = []
        self.filename = filename
        self.lazy = True if filename is not None else False
        self.raise_ioerror_on_load = True

    def __getitem__(self, key):
        """Get the state with specified key
        """
        try:
            value = super(State, self).__getitem__(key)
            if value is UNLOADED:
                raise KeyError("Value for '%s' not loaded yet" % key)
            elif value is DELETED:
                raise KeyError("Value for '%s' has been deleted" % key)
        except KeyError:
            if self.lazy:
                if self.filename is None:
                    raise
                # Try to get the section from file
                try:
                    with h5py.File(self.filename, "r") as h5file:
                        h5name = "state/" + "/".join(key.split("."))
                        value = pickle.loads(h5file[h5name].value)
                        self.__setitem__(key, value)
                except IOError as err:
                    if self.raise_ioerror_on_load:
                        raise IOError(
                            "Cannot load state from file '%s',"
                            "(err: '%s')" % (
                                self.filename, err))
                    else:
                        log.debug(
                            "Tried to load state from '%s' "
                            "but failed." % self.filename)
                        raise KeyError("Could not load key '%s' "
                                       "from file '%s', "
                                       "IOError ('%s')" % (
                                           key, self.filename, err))
            else:
                raise

        return value

    def __setitem__(self, key, value):
        """Stores state with key and value
        """
        super(State, self).__setitem__(key, value)
        self.changed.append(key)

    def __delitem__(self, key):
        """Delete a key from the state
        """
        super(State, self).__delitem__(key)
        self[key] = DELETED

    def __iter__(self):
        """Overload HierarchicalOrderedDict's __iter__
        """
        if self.base is None:
            return super(State, self).__iter__()

        return super(State, self).__iter__()

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
                if not self.lazy:
                    os.rename(filename, dfn)
                else:
                    if self.filename == filename:
                        shutil.copyfile(filename, dfn)
                    else:
                        os.rename(filename, dfn)
                        shutil.copyfile(self.filename, filename)

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

                            if value is not DELETED and value is not UNLOADED:
                                # Pickle and save
                                pickled_state = pickle.dumps(value)
                                pickled_state_array = np.array(pickled_state)
                                h5file.create_dataset(
                                    group.name + "/" + key,
                                    data=pickled_state_array)
                            elif value is DELETED:
                                del level[key]

                save_level_to_group(self.base, state_grp)
                self.changed = []

        except IOError as err:
            raise IOError("Cannot save state to file '%s', (err: '%s')",
                          filename,
                          err)

    def load(self,
             filename=None,
             lazy=True,
             raise_error=True):
        """Loads state from a h5f file
        """
        # Reset state
        self.base = OrderedDict()
        self.changed = []
        self.raise_ioerror_on_load = raise_error
        self.lazy = lazy

        if filename is not None:
            # Load the data later when it's needed
            self.filename = filename
        elif filename is None and self.filename is None:
            raise RuntimeError(
                "Need filename to load data")
        else:
            filename = self.filename

        try:
            with h5py.File(filename, 'r') as h5file:
                log.info("Loading state from file '%s'", filename)

                def load(group, level):
                    """Loads a whole h5 file as an Ordered dict
                    """
                    for key, value in group.items():
                        if isinstance(value, h5py.Group):
                            if key not in level:
                                level[key] = OrderedDict()
                            load(value, level[key])
                        elif not lazy:
                            level[key] = pickle.loads(value.value)
                        else:
                            level[key] = UNLOADED
                load(h5file['state'], self.base)

        except IOError as err:
            if self.raise_ioerror_on_load:
                raise IOError(
                    "Cannot load state from file '%s',"
                    " (err: '%s')" % (filename, err))
            else:
                log.debug(
                    "Tried to load state from '%s' "
                    "but failed." % self.filename)

    def show(self):
        """Shows the state
        """
        if self.lazy:
            self.load(lazy=False)
        super(State, self).show()
