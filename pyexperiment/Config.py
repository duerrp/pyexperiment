"""Provides an easy way to configure a python application. Basically
implements a singleton configuration at module level.

Basic usage: Load the (singleton) configuration with load, access the
values like you would in a dictionary.

Written by Peter Duerr.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
import configobj
import validate

from pyexperiment.utils.Singleton import Singleton
from pyexperiment.utils.DotSeparatedNestedMapping \
    import DotSeparatedNestedMapping


class Config(DotSeparatedNestedMapping,  # pylint: disable=too-many-ancestors
             Singleton):
    """Represents a singleton configuration object.
    """
    CONFIG_SPEC_PATH = 'configspec.ini'
    """Path of the file with the specification for configurations.
    """

    @classmethod
    def _new_section(cls):
        """Creates a new section Mapping
        """
        return configobj.Section()

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        return isinstance(obj, configobj.Section)

    def __init__(self):
        """Initializer
        """
        # Members will be initialized by load later
        super(Config, self).__init__()
        self.read_from_file = None
        self.filename = None

    def override_with_args(self, config, options=None):
        """Override configuration with command line arguments and validate
        against specification.
        """
        # Override options with command line arguments
        if options is not None:
            for key, value in options:
                config_level = config
                split_key = key.split('.')
                if len(split_key) == 1:
                    if 'basic' not in config:
                        config['basic'] = configobj.Section(config_level, 1,
                                                            config, {})
                    config['basic'][key] = value
                else:
                    depth = 1
                    while len(split_key) > 1:
                        if not split_key[0] in config_level:
                            config_level[split_key[0]] \
                                = configobj.Section(
                                    config_level, depth, config, {})
                        else:
                            pass
                        config_level = config_level[split_key[0]]
                        split_key = split_key[1:]
                        depth += 1
                    config_level[split_key[0]] = value

        # Validate it
        validator = validate.Validator()
        result = config.validate(validator, copy=True, preserve_errors=True)

        if not isinstance(result, bool):
            raise RuntimeError("Configuration does not adhere"
                               " to the specification: %s" %
                               configobj.flatten_errors(self.base, result))
        else:
            if result:
                return config
            else:
                raise RuntimeError("Something strange going on...")

    def load(self, filename,
             spec_filename=CONFIG_SPEC_PATH,
             options=None,
             default_spec=None):
        """Loads a configuration from filename (or string). Missing values
        will be read from the specification file or string.
        """
        # Check if config file exists
        read_from_file = os.path.isfile(filename)
        if read_from_file:
            self.filename = filename

        # Create the configuration (overriding the default with user
        # specs if necessary)
        user_config = configobj.ConfigObj(filename, configspec=spec_filename)
        user_config = self.override_with_args(user_config, options)
        if default_spec is not None:
            default_config = configobj.ConfigObj(filename,
                                                 configspec=default_spec)
            default_config = self.override_with_args(default_config, options)

            default_config.merge(user_config)
            self.base = default_config
        else:
            self.base = user_config

        # Add some more info
        self.base.read_from_file = read_from_file

    def save(self, filename):
        """Write configuration to file
        """
        if self.base is None:
            raise RuntimeError(
                "Configuration not initialized yet (call load first).")
        else:
            if filename is None:
                print("Too few arguments (provide filename for configuration)")
                return
            with open(filename, 'wb') as outfile:
                self.base.write(outfile)

    # def b__len__(self):
    #     """Get the number of configuration items
    #     """
    #     if self.config is not None:
    #         return len(self.config)
    #     else:
    #         return 0

    # def __iter__(self):
    #     """Returns an iterator over the configuration
    #     """
    #     return iter(self.config)

    # def __getitem__(self, name):
    #     """Get configuration item. The name should be of the form
    #     section.subsection...item
    #     """
    #     if self.config is None:
    #         raise RuntimeError("Configuration not loaded yet")
    #     else:
    #         split_name = name.split(".")
    #         level = 0
    #         section = self.config
    #         while level < len(split_name) - 1:
    #             try:
    #                 section = section[split_name[level]]
    #                 level += 1
    #             except AttributeError as err:
    #                 raise AttributeError(
    #                     "Configuration does not contain section '%s',"
    #                     " (err: '%s')", ".".join(level[0:level]), err)
    #         try:
    #             value = section[split_name[level]]
    #         except AttributeError as err:
    #             raise AttributeError(
    #                 "Configuration does not contain value '%s', (err: '%s')",
    #                 name, err)
    #         return value

    # def __setitem__(self, name, value):
    #     """Set configuration item
    #     """
    #     raise NotImplementedError("Not implemented yet. Cannot set %s -> %s",
    #                               name, value)

    # def __delitem__(self, name):
    #     """Delete configuration item
    #     """
    #     raise NotImplementedError(
    #         "Not implemented yet. Cannot delete %s -> %s", name)

    # def __repr__(self):
    #     """Pretty print the configuration
    #     """
    #     repr_str = ''
    #     if self.read_from_file:
    #         repr_str += "Configuration read from '%s':\n" % self.filename
    #     else:
    #         repr_str += "Configuration created from specs:\n"

    #     def repr_section(dictionary, prefix=""):
    #         """Print a section of the configuration
    #         """
    #         repr_str = ''
    #         for key in dictionary.keys():
    #             if isinstance(dictionary[key], configobj.Section):
    #                 repr_str += prefix + key + '\n'
    #                 repr_str += repr_section(dictionary[key], prefix + '  ')
    #             else:
    #                 repr_str += (
    #                     prefix + key + ' = ' + repr(dictionary[key]) + '\n'
    #                 )

    #         return repr_str

    #     repr_str += repr_section(self.config)
    #     return repr_str
