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
from toolz import thread_first

from pyexperiment.utils.Singleton import DefaultSingleton
from pyexperiment.utils.Singleton import delegate_singleton
from pyexperiment.Logger import TimingLogger
from pyexperiment.utils.HierarchicalMapping import HierarchicalMapping
from pyexperiment.utils.HierarchicalMapping import HierarchicalOrderedDict
from pyexperiment.utils.config_conversion import ohm_to_spec
from pyexperiment.utils.config_conversion import convert_spec
from pyexperiment.utils.config_conversion import conf_to_ohm
from pyexperiment.utils.config_conversion import ohm_to_spec_list


log = delegate_singleton(TimingLogger)  # pylint: disable=invalid-name
"""Pyexperiment's logger, re-wrapped here to avoid cyclical dependency
"""


class Config(HierarchicalMapping,  # pylint: disable=too-many-ancestors
             DefaultSingleton):
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
                 spec=CONFIG_SPEC_PATH,
                 options=None,
                 default_spec=None):
        """Initializer
        """
        super(Config, self).__init__()
        self.read_from_file = None
        self.filename = None

        # Merge specs, giving precedence to user spec, then, before_init_spec,
        # then default_spec
        if ((spec == self.CONFIG_SPEC_PATH and
             not os.path.isfile(self.CONFIG_SPEC_PATH))):
            spec = None

        user_spec_ohm = thread_first(spec, convert_spec, conf_to_ohm)
        before_init_spec_ohm = thread_first(self.DEFAULT_CONFIG,
                                            ohm_to_spec,
                                            convert_spec,
                                            conf_to_ohm)
        default_spec_ohm = thread_first(default_spec,
                                        convert_spec,
                                        conf_to_ohm)

        user_spec_ohm.merge(before_init_spec_ohm)
        user_spec_ohm.merge(default_spec_ohm)
        full_spec = ohm_to_spec_list(user_spec_ohm)

        # Load the configuration and overload it with the options
        if filename is not None:
            self.load(filename,
                      full_spec,
                      options)
        else:
            self.base = configobj.ConfigObj()

        # Unless the options are already there, overload them with the defaults
        # set before initialization
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self:
                self[key] = value

    def override_with_args(self, options):
        """Override configuration with option dictionary
        """
        for key, value in options:
            self[key] = value

    @staticmethod
    def validate_config(config):
        """Validate configuration
        """
        validator = validate.Validator()
        result = config.validate(validator,
                                 copy=True,
                                 preserve_errors=True)

        if not isinstance(result, bool):
            raise ValueError("Configuration does not adhere"
                             " to the specification: %s" %
                             configobj.flatten_errors(config, result))
        elif not result:
            # This should never happen
            raise RuntimeError(  # pragma: no cover
                "Configuration validated to false.")

    def load(self,
             filename,
             spec=None,
             options=None):
        """Loads a configuration from filename (or string). Missing values
        will be read from the specification file or string.
        """
        # Check if config file exists
        read_from_file = os.path.isfile(filename)
        if read_from_file:
            self.filename = filename

        # Create the configuration (overriding the default with user
        # specs if necessary)
        self.base = configobj.ConfigObj(filename, configspec=spec)

        # Override options
        if options is not None:
            self.override_with_args(options)

        # Validate the configuration
        if spec is not None:
            self.validate_config(self.base)

        # Add some more info
        self.base.read_from_file = read_from_file

    def save(self, filename):
        """Write configuration to file
        """
        if self.base is None:
            # This should never happen
            raise RuntimeError(  # pragma: no cover
                "Configuration not initialized yet.")
        else:
            with open(filename, 'wb') as outfile:
                self.base.write(outfile)
