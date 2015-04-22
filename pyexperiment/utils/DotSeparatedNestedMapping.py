"""Provide flat, point separated interface to nested mapping
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

# Python 3 compatibility
from six import iteritems


from collections import MutableMapping, OrderedDict
import unittest


class DotSeparatedNestedMapping(MutableMapping):
    def __init__(self, container_type):
        """Initializer
        """
        self.container_type = container_type
        self.base = self.container_type()

    def __descend_sections(self, key, create=False):
        """Traverse the nested containers down to the last layer
        """
        try:
            split_name = key.split(".")
        except AttributeError() as err:
            raise KeyError("Key must be a string ('%s')", err)
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
                        "Section '%s' does not exist"
                        " ('%s')" % (split_name[level], err))
                else:
                    section[split_name[level]] = self.container_type()
                    section = section[split_name[level]]
                    level += 1

        subkey = split_name[level]
        return section, subkey

    def __getitem__(self, key):
        section, subkey = self.__descend_sections(key)
        # At the last section, get the value
        try:
            value = section[subkey]
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)
        return value

    def __setitem__(self, key, value):
        section, subkey = self.__descend_sections(key, create=True)
        # At the last section, set the value
        try:
            section[subkey] = value
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)

    def __delitem__(self, key):
        section, subkey = self.__descend_sections(key)
        # At the last section, set the value
        try:
            del section[subkey]
        except KeyError as err:
            raise KeyError(
                "Key does not exist '%s' ('%s')",
                key, err)

    def __iter__(self):
        """Need to define __iter__ to make it a MutableMapping
        """
        iterator_list = [(iteritems(self.base), '')]
        while iterator_list:
            iterator, prefix = iterator_list.pop()
            try:
                key, value = next(iterator)
                if len(prefix) > 0:
                    key = prefix + '.' + key
            except StopIteration:
                continue
            iterator_list.append((iterator, prefix))

            if isinstance(value, self.container_type):
                iterator_list.append((iteritems(value), key))
            else:
                yield key

    def __len__(self):
        return len(list(iter(self)))

    def __repr__(self):
        return repr(list(self.items()))
