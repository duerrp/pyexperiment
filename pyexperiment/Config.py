"""Provides an easy way to configure a python application. Basically

implements a singleton configuration at module level.

The configuration is based on the configobj library, but wrapped with
convenience functions that make handling configurations much simpler.

Basic usage: Load the (``Singleton``) configuration with load, access
the values like you would in a dictionary.

If the singleton is accessed before being loaded, it behaves like an
``HierarchicalOrderedDict``. Values stored in this ``DEFAULT_CONFIG``,
are used to override values not set by load, i.e., if load is called
after values are set on an uninitialized configuration, the values in
the configuration persist. Moreover, saving an uninitialized
configuration will work as expected.

Written by Peter Duerr.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import os
import configobj
import validate

from pyexperiment.utils.Singleton import InitializeableSingleton
from pyexperiment.utils.Singleton import InitializeableSingletonIndirector
from pyexperiment.Logger import TimingLogger
from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalMapping
from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalOrderedDict

log = InitializeableSingletonIndirector(  # pylint: disable=invalid-name
    TimingLogger)
"""Pyexperiment's logger, re-wrapped here to avoid cyclical dependency
"""


class Config(HierarchicalMapping,  # pylint: disable=too-many-ancestors
             InitializeableSingleton):
    """Represents a singleton configuration object.
    """
    CONFIG_SPEC_PATH = 'configspec.ini'
    """Path of the file with the specification for configurations.
    """

    DEFAULT_CONFIG = HierarchicalOrderedDict()
    """Default configuration, later used by initialize
    """

    @classmethod
    def _is_section(cls, obj):
        """Returns true if obj is a section
        """
        return isinstance(obj, configobj.Section)

    @classmethod
    def reset_instance(cls):
        """Overloads reset_instance to reset the DEFAULT_CONFIG
        """
        cls.DEFAULT_CONFIG = HierarchicalOrderedDict()
        super(Config, cls).reset_instance()

    @classmethod
    def _get_pseudo_instance(cls):
        """Overloaded method returning the DEFAULT_CONFIG with added methods
        """
        def save_unitialized(filename):
            """Saves an unitialized config
            """
            cls.initialize()
            cls.get_instance().save(filename)

        cls.DEFAULT_CONFIG.reset_instance = Config.reset_instance
        cls.DEFAULT_CONFIG.load = cls.initialize
        cls.DEFAULT_CONFIG.save = save_unitialized

        return cls.DEFAULT_CONFIG

    def _new_section(self, parent, level):
        """Creates a new section Mapping
        """
        return configobj.Section(parent, level, self.base)

    def __init__(self,
                 filename=None,
                 spec_filename=CONFIG_SPEC_PATH,
                 options=None,
                 default_spec=None):
        """Initializer
        """
        super(Config, self).__init__()
        self.read_from_file = None
        self.filename = None

        # Load the configuration and overload it with the options
        if filename is not None:
            self.load(filename,
                      spec_filename,
                      options,
                      default_spec)
        else:
            self.base = configobj.ConfigObj()

        # Unless the options are already there, overload them with the defaults
        # set before initialization
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.base:
                self.base[key] = value

    @staticmethod
    def override_with_args(config,
                           options=None,
                           do_validate=True):
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

        # Validate it if necessary
        if do_validate:
            validator = validate.Validator()
            result = config.validate(validator,
                                     copy=True,
                                     preserve_errors=True)

            if not isinstance(result, bool):
                raise ValueError("Configuration does not adhere"
                                 " to the specification: %s" %
                                 configobj.flatten_errors(config, result))
            elif not result:
                raise RuntimeError("Configuration validated to false.")

        return config

    def load(self,
             filename,
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

        # Check if spec is default, if yes, make sure it exists
        if spec_filename == self.CONFIG_SPEC_PATH:
            if not os.path.isfile(spec_filename):
                log.debug("No config spec found at default location '%s'",
                          self.CONFIG_SPEC_PATH)
                spec_filename = None

        # Create the configuration (overriding the default with user
        # specs if necessary)
        user_config = configobj.ConfigObj(filename, configspec=spec_filename)
        user_config = self.override_with_args(
            user_config,
            options,
            do_validate=spec_filename is not None)
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
                "Configuration not initialized yet.")
        else:
            with open(filename, 'wb') as outfile:
                self.base.write(outfile)
