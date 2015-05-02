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
from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalMapping


class Config(HierarchicalMapping,  # pylint: disable=too-many-ancestors
             Singleton):
    """Represents a singleton configuration object.
    """
    CONFIG_SPEC_PATH = 'configspec.ini'
    """Path of the file with the specification for configurations.
    """

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        return isinstance(obj, configobj.Section)

    def _new_section(self, parent, level):
        """Creates a new section Mapping
        """
        return configobj.Section(parent, level, self.base)

    def __init__(self):
        """Initializer
        """
        # Members will be initialized by load later
        super(Config, self).__init__()
        self.read_from_file = None
        self.filename = None

    @staticmethod
    def override_with_args(config, options=None):
        """Override configuration with command line arguments and validate
        against specification.
        """
        # Override options with command line arguments
        if options is not None:
            for key, value in options:
                config_level = config
                split_key = key.split('.')
                if len(split_key) == 1:
                    config[key] = value
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
            raise ValueError("Configuration does not adhere"
                             " to the specification: %s" %
                             configobj.flatten_errors(config, result))
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
