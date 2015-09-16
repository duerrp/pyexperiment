"""Handles persistent state for an experiment.

Based on a `HierarchicalOrderedDict`, the `State` singleton handles
global, persistent state, allowing to save and load state from h5f
files. Numpy arrays are saved in native h5f format so that they can be
loaded by other programs, other python objects are saved in pickled
format.

Lazy loading (by default), means that values of the state are not loaded
until they are first accessed.

Note that keys for the state should not contain slashes.

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
    from six.moves import filter  # pylint: disable=redefined-builtin

from six import string_types

import numpy as np
import h5py
import os
import shutil
from collections import OrderedDict
from functools import partial
import lockfile

from pyexperiment.utils.Singleton import Singleton
from pyexperiment.utils.Singleton import delegate_singleton
from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalOrderedDict
from pyexperiment.utils import sentinel
from pyexperiment.Logger import TimingLogger
from pyexperiment.utils.functional import starts_with

log = delegate_singleton(TimingLogger)  # pylint: disable=invalid-name
"""Pyexperiment's logger, re-wrapped here to avoid cyclical dependency
"""


DELETED = sentinel.create('DELETED', 'Deleted State')
UNLOADED = sentinel.create('UNLOADED', 'Unloaded State')


class State(Singleton,  # pylint: disable=too-many-ancestors
            HierarchicalOrderedDict):
    """Represents persistent state of an experiment.
    """
    def __init__(self, filename=None):
        """Initializer
        """
        super(State, self).__init__()

        # Keep track of changed values
        self.changed = set()
        self.filename = filename
        self.lazy = True if filename is not None else False
        self.raise_ioerror_on_load = True

    def __load_from_file(self, key):
        """Try to get a value from disk
        """
        try:
            with h5py.File(self.filename, "r") as h5file:
                h5name = "state/" + "/".join(key.split(self.SECTION_SEPARATOR))
                if not isinstance(h5file[h5name], h5py.Group):
                    if (('type' in h5file[h5name].attrs
                         and h5file[h5name].attrs['type'] == 'ndarray')):
                        value = h5file[h5name].value
                    else:  # must be a pickled array
                        value = pickle.loads(h5file[h5name].value.tostring())
                    self.__setitem__(key, value)
                    self.changed.remove(key)
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

        return value

    def __getitem__(self, key):
        """Get the state with specified key
        """
        try:
            value = super(State, self).__getitem__(key)
            if value is UNLOADED:
                raise KeyError("Value for '%s' not loaded yet" % key)
            # Make sure all the values in the ordered dict are loaded
            if self.lazy and isinstance(value, OrderedDict):
                def is_descendant(superkey, key):
                    """Returns true if key is a descendant of superkey
                    """
                    split_super = superkey.split(self.SECTION_SEPARATOR)
                    split_key = key.split(self.SECTION_SEPARATOR)

                    return starts_with(split_super, split_key)

                descendants = filter(partial(is_descendant, key),
                                     self.keys())
                for descendant in descendants:
                    self.__load_from_file(descendant)

                value = super(State, self).__getitem__(key)

        except KeyError:
            if self.lazy:
                if self.filename is None:
                    raise RuntimeError(
                        "Cannot load state lazily without filename")
                value = self.__load_from_file(key)
            else:
                raise

        if value is DELETED:
            raise KeyError("Value for '%s' has been deleted" % key)

        return value

    def __setitem__(self, key, value):
        """Stores state with key and value
        """
        if isinstance(key, string_types) and "/" in key:
            raise ValueError("entries in state should not have '/' character")
        super(State, self).__setitem__(key, value)
        self.changed.add(key)

    def __delitem__(self, key):
        """Delete a key from the state
        """
        super(State, self).__delitem__(key)
        self[key] = DELETED

    def __iter__(self):
        """Overload HierarchicalOrderedDict's __iter__
        """
        # Use filter with super's __getitem__ to exclude deleted keys
        return filter(lambda x: super(State, self).__getitem__(x)
                      is not DELETED,
                      super(State, self).__iter__())

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
            log.debug("No need to save empty state")
            return False
        if not self.changed:
            log.debug("No need to save unchanged state")
            return False

        # Otherwise
        return True

    def save(self,
             filename,
             rotate_n_state_files=0,
             compression_level=5):
        """Saves state to a h5f file, rotating if necessary
        """
        if not self.need_saving():
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
                            if key in group and value is not UNLOADED:
                                del group[key]

                            if value is not DELETED and value is not UNLOADED:
                                if isinstance(value, np.ndarray):
                                    state_array = value
                                    ds_type = 'ndarray'
                                else:
                                    # Pickle the data
                                    pickled_state = pickle.dumps(
                                        value,
                                        protocol=pickle.HIGHEST_PROTOCOL)
                                    state_array = np.fromstring(pickled_state,
                                                                dtype=np.uint8)
                                    ds_type = 'pickle'

                                dataset = h5file.create_dataset(
                                    group.name + "/" + key,
                                    data=state_array,
                                    compression='gzip',
                                    compression_opts=compression_level,
                                    shuffle=True,
                                )
                                dataset.attrs['type'] = ds_type
                            elif value is DELETED:
                                del level[key]

                save_level_to_group(self.base, state_grp)
                self.changed = set()

        except IOError as err:
            raise IOError("Cannot save state to file '%s', (err: '%s')" % (
                filename, err))

    def __setup_sections_from_file(self, filename):
        """Convert groups from h5 file to sections of the mapping
        """
        with h5py.File(filename, 'r') as h5file:
            log.info("Loading state from file '%s'", filename)

            def load_sections(group, level):
                """Loads sections of h5 file as Ordered dicts
                """
                for key, value in group.items():
                    if isinstance(value, h5py.Group):
                        if key not in level:
                            level[key] = OrderedDict()
                        load_sections(value, level[key])
                    else:
                        level[key] = UNLOADED

            self.base = OrderedDict()
            load_sections(h5file['state'], self.base)

    def load(self,
             filename=None,
             lazy=True,
             raise_error=True):
        """Loads state from a h5f file
        """
        # Reset state
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
            self.__setup_sections_from_file(filename)
            if not self.lazy:
                for key in self.keys():
                    self.__load_from_file(key)
            self.changed = set()
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
            self.load(lazy=False, raise_error=False)
        super(State, self).show()


class StateHandler(object):
    """Provides a save environment for using the state
    """
    STATE_LOCK_TIMEOUT = 10
    """Maximal time allowed to acquire the state file's lock (if specified
    in the configuration)
    """

    COMPRESSION_LEVEL = 5
    """Compression level used for saving the state
    """

    def __init__(self,
                 filename,
                 load=False,
                 save=False,
                 rotate_n_files=0):
        """Initializer
        """
        self.filename = filename
        self.load = load
        self.save = save
        self.state_lock = None
        self.rotate_n_files = int(rotate_n_files)

    def lock(self):
        """Lock the state file
        """
        self.state_lock = lockfile.FileLock(self.filename)
        try:
            self.state_lock.acquire(timeout=self.STATE_LOCK_TIMEOUT)
        except lockfile.LockTimeout:
            raise RuntimeError("Cannot acquire lock on state file ('%s'), "
                               "check if another process is using it"
                               % self.filename)

    def unlock(self):
        """Unlock the state file
        """
        self.state_lock.release()
        self.state_lock = None

    def __enter__(self):
        """Enter method for 'with' block
        """
        # If necessary, lock the state file and load the state
        if self.load:
            self.lock()
            State.get_instance().load(self.filename,
                                      lazy=True,
                                      raise_error=False)

        return self

    def __exit__(self, *args, **kwargs):
        """Exit method for the 'with' block
        """
        try:
            # If necessary lock the state and save
            if self.save:
                if self.state_lock is None:
                    self.lock()

                State.get_instance().save(
                    self.filename,
                    self.rotate_n_files,
                    compression_level=self.COMPRESSION_LEVEL)

        finally:
            # Release the state lock if we have it
            if self.state_lock is not None:
                self.unlock()
