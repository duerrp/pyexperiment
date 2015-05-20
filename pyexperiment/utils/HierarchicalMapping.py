"""Provide flat, point separated interface to nested mappings

As the zen of python says, flat is better than nested. In many cases,
however, it makes sense to store data in a nested data structure. To
bridge the gap, the HierarchicalMapping defines an abstract base class
for data structures that can be treated like an ordinary mapping from
strings to values, but with the advantage that the values for keys
containing a level separator, e.g., "level1.level2.level3" are stored in
a nested hierarchy of mappings.

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Python 3 compatibility
from six import iteritems

from collections import MutableMapping
from collections import OrderedDict
from toolz import count, thread_first


class HierarchicalMapping(  # pylint: disable=too-many-ancestors
        MutableMapping):
    """ABC for flat mutable mappings where all keys are strings.

    Levels of hierarchy are indicated by a separator character and the
    storage is implemented as a hierarchy of nested Mutable mappings.
    """
    SECTION_SEPARATOR = "."
    """Separates the hierarchy levels
    """

    @classmethod
    def _new_section(cls, parent, level):
        """Creates a new section Mapping
        """
        raise NotImplementedError("Subclass should implement this")

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        raise NotImplementedError("Subclass should implement this")

    def __init__(self):
        """Initializer
        """
        self.base = None

    def __descend_sections(self, key, create=False):
        """Traverse the nested mappings down to the last layer
        """
        if self.base is None:
            raise KeyError("Cannot access key in empty mapping")
        try:
            split_name = key.split(self.SECTION_SEPARATOR)
        except AttributeError as err:
            raise TypeError("Key must be a string ('%s')" % err)
        level = 0
        section = self.base
        # Iterate through the sections
        while level < len(split_name) - 1:
            try:
                section = section[split_name[level]]
                level += 1
            except KeyError as err:
                if not create:
                    raise KeyError(
                        "Section '%s' does not exist in '%s'" % (
                            split_name[level],
                            self.SECTION_SEPARATOR.join(split_name[:level])))
                else:
                    section[split_name[level]] = self._new_section(section,
                                                                   level)
                    section = section[split_name[level]]
                    level += 1

        subkey = split_name[level]
        return section, subkey

    def __getitem__(self, key):
        """Get an item
        """
        section, subkey = self.__descend_sections(key)
        # At the last section, get the value
        try:
            value = section[subkey]
        except KeyError as _err:
            raise KeyError(
                "Key '%s' does not exist" % key)
        return value

    def __setitem__(self, key, value):
        """Set an item
        """
        if self.base is None:
            raise KeyError("Mapping has not been initialized")
        section, subkey = self.__descend_sections(key, create=True)
        # At the last section, set the value
        section[subkey] = value

    def __delitem__(self, key):
        """Delete an item
        """
        section, subkey = self.__descend_sections(key)
        # At the last section, set the value
        try:
            del section[subkey]
        except KeyError as _err:
            raise KeyError(
                "Key does not exist '%s'" % key)

    def __iter__(self):
        """Need to define __iter__ to make it a MutableMapping
        """
        iterator_list = [(iteritems(self.base or {}), '')]
        while iterator_list:
            iterator, prefix = iterator_list.pop()
            try:
                key, value = next(iterator)
                if len(prefix) > 0:
                    key = prefix + '.' + key
            except StopIteration:
                continue
            iterator_list.append((iterator, prefix))

            if self._is_section(value):
                iterator_list.append((iteritems(value), key))
            else:
                yield key

    def __len__(self):
        """Returns the number of entries in the mapping"""
        return count(iter(self))

    def __repr__(self):
        """Get a representation of the mapping"""
        return thread_first(self, iteritems, list, repr)

    def base_keys(self):
        """Returns the keys of the first level of the mapping
        """
        return self.base.keys()

    def section_keys(self):
        """Returns the keys of the sections (and subsections) of the mapping
        """
        seen = set()
        seen_add = seen.add
        for element in (key.split(self.SECTION_SEPARATOR)
                        for key in self.keys()):
            if len(element) > 1:
                section = self.SECTION_SEPARATOR.join(element[:-1])
                if section not in seen:
                    seen_add(section)
                    yield section

    def get(self, key, default=None):
        """Get the key or return the default value if provided
        """
        try:
            return self[key]
        except KeyError:
            if default is not None:
                return default
            else:
                raise

    def get_or_set(self, key, value):
        """Either gets the value associated with key or set it
        This can be useful as an easy way of
        """
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    def show(self):
        """Pretty-prints the content of the mapping
        """
        def show_section(section, prefix):
            """Show a sub-section of the mapping
            """
            for key, value in section.items():
                if self._is_section(value):
                    # Go to next level
                    print(prefix + "[" + key + "]")
                    show_section(section[key], prefix + "  ")
                else:
                    print(prefix + str(key) + ":" + repr(value))

        show_section(self.base, " ")

    def merge(self, other):
        """Merge in another mapping, giving precedence to self
        """
        for key, value in other.items():
            if key not in self:
                self[key] = value


class HierarchicalOrderedDict(  # pylint: disable=too-many-ancestors
        HierarchicalMapping):
    """Instance of the HierarchicalMapping based on an OrderedDict.
    """
    @classmethod
    def _new_section(cls, _parent, _level):
        """Creates a new section Mapping
        """
        return OrderedDict()

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        return isinstance(obj, OrderedDict)

    def __init__(self):
        """Initializer
        """
        super(HierarchicalOrderedDict, self).__init__()
        self.base = OrderedDict()


class HierarchicalDict(  # pylint: disable=too-many-ancestors
        HierarchicalMapping):
    """Instance of the ``HierarchicalMapping`` based on ``dict``
    """
    @classmethod
    def _new_section(cls, _parent, _level):
        """Creates a new section Mapping
        """
        return dict()

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        return isinstance(obj, dict)

    def __init__(self):
        """Initializer
        """
        super(HierarchicalDict, self).__init__()
        self.base = dict()
