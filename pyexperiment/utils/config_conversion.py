"""Utility functions to convert config specs to OrderedHierarchicalMappings

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import six
import configobj
from collections import defaultdict
from itertools import count as count_up
from toolz import remove

from pyexperiment.utils.HierarchicalMapping import HierarchicalOrderedDict


def convert_spec(spec):
    """Convert spec (string or filename) to ConfigObj
    """
    config = configobj.ConfigObj(configspec=spec)

    return config.configspec


def conf_to_ohm(conf, ohm=None, section_name=''):
    """Converts a configobj to an OrderedHierarchicalMapping
    """
    if conf is None:
        return HierarchicalOrderedDict()

    if ohm is None:
        ohm = HierarchicalOrderedDict()

    for key, value in conf.items():
        if not section_name == '':
            new_key = (section_name +
                       HierarchicalOrderedDict.SECTION_SEPARATOR +
                       key)
        else:
            new_key = key
        if not isinstance(value, configobj.Section):
            ohm[new_key] = value
        else:
            conf_to_ohm(value,
                        ohm=ohm,
                        section_name=new_key)
    return ohm


def sort_ohm(ohm):
    """Sorts an OrderedHierarchicalMapping
    """
    first_level = lambda k: len(k[0].split(ohm.SECTION_SEPARATOR)) == 1
    leveled_items = remove(first_level, ohm.items())
    first_level_items = [item for item in ohm.items() if first_level(item)]
    return first_level_items + sorted(leveled_items,
                                      key=lambda k: k[0].split(
                                          ohm.SECTION_SEPARATOR))


def ohm_to_spec_list(ohm, value_transform=lambda x: x):
    """Convert OrderedHierarchicalMapping to specification list

    The value_transform argument should be a function that transforms
    the values of the ohm to the entries of the spec list.
    """
    spec = []
    level_start = "["
    level_stop = "]"

    sorted_items = sort_ohm(ohm)

    def skip_to_header(spec, section_header):
        """Skips to the next header"""
        index = spec.index(section_header)
        for elem in spec[index:]:
            if not elem[0] == six.b('[')[0]:
                continue
            else:
                index += 1
        return index

    for key, value in sorted_items:
        split_key = key.split(ohm.SECTION_SEPARATOR)
        index = None
        if len(split_key) > 1:
            for level, part in zip(count_up(1), split_key[:-1]):
                section_header = (level * level_start +
                                  part +
                                  level*level_stop).encode()
                if section_header in spec:
                    index = skip_to_header(spec, section_header)
                    continue
                else:
                    spec += [section_header]
                    index = skip_to_header(spec, section_header)

        spec_entry = (split_key[-1] +
                      " = " +
                      value_transform(value))
        if index is None:
            spec += [spec_entry.encode()]
        else:
            spec.insert(index + 1, spec_entry.encode())
    return spec


def ohm_to_spec(ohm):
    """Creates a config spec from an OrderedHierarchicalMapping
    """
    spec_type = defaultdict(lambda: "string",
                            [(type(3), "integer"),
                             (type("bla"), "string"),
                             (type(True), "boolean"),
                             (type(3.14), "float"),
                             (tuple, "tuple")])

    value_transform = lambda value: (spec_type[type(value)] +
                                     ("(default=%s)" % value
                                      if not (isinstance(value, tuple) or
                                              isinstance(value, list))
                                      else "(default=list%s)" % str(
                                          tuple(value))))

    return ohm_to_spec_list(ohm, value_transform)
