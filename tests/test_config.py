"""Tests the conf module of pyexperiment

Written by Peter Duerr
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
import tempfile
import os

from pyexperiment import conf


class TestConf(unittest.TestCase):
    """Test the conf module's basic functions
    """
    def tearDown(self):
        """Tear down the test fixture
        """
        conf.reset_instance()

    def test_empty_conf(self):
        """Test empty config throws Exception
        """
        conf.reset_instance()
        self.assertRaises(KeyError, conf.__getitem__, 'a')

    def test_empty_initialized_conf(self):
        """Test empty config throws Exception even after initialization
        """
        conf.reset_instance()
        conf.initialize()
        self.assertRaises(KeyError, conf.__getitem__, 'a')

    def test_save_no_config(self):
        """Test saving uninitialized config
        """
        conf['a'] = 12
        with tempfile.NamedTemporaryFile() as temp:
            conf.save(temp.name)
            conf.reset_instance()
            self.assertNotIn('a', conf)
            conf.load(temp.name)
            self.assertIn('a', conf)
            self.assertEqual(int(conf['a']), 12)

    def test_in(self):
        """Test the `in` function works for config
        """
        conf.initialize()
        conf['section_1.a'] = 12
        self.assertTrue('section_1.a' in conf)
        self.assertFalse('section_1.f' in conf)

    def test_in_uninitialized(self):
        """Test the `in` function works for config
        """
        conf['section_1.a'] = 12
        self.assertTrue('section_1.a' in conf)
        self.assertFalse('section_1.f' in conf)

    def test_get_default(self):
        """Test getting config values with a default argument
        """
        self.assertRaises(KeyError, conf.__getitem__, 'a')
        self.assertRaises(KeyError, conf.get, 'a')
        self.assertEqual(conf.get('a', default=12), 12)
        self.assertRaises(KeyError, conf.get, 'a')

    def test_initialize(self):
        """Test initializing uninitialized config
        """
        conf['a'] = 12
        conf.initialize()
        self.assertEqual(conf['a'], 12)


class TestConfFile(unittest.TestCase):
    """Test the conf module with a configuration file
    """
    TEST_CONFIG = ("[section_1]\n"
                   "a = 12\n"
                   "b = 13\n"
                   "[section_2]\n"
                   "c = True")

    def setUp(self):
        """Setup the test fixture
        """
        self.filename = tempfile.mkstemp()[1]
        with open(self.filename, 'w') as outfile:
            outfile.write(self.TEST_CONFIG)

    def tearDown(self):
        """Tear down the test fixture
        """
        conf.reset_instance()
        os.remove(self.filename)

    def test_initialize_with_file(self):
        """Test initializing uninitialized config with a file
        """
        conf['a'] = 12
        conf['section_1.a'] = 13
        self.assertEqual(conf['a'], 12)
        self.assertEqual(conf['section_1.a'], 13)

        conf.initialize(self.filename)
        self.assertEqual(conf['a'], 12)
        self.assertEqual(conf['section_1.a'], 12)

    def test_initialize_with_spec(self):
        """Test initializing uninitialized config with a spec
        """
        spec = ("[section_1]\n"
                "d = integer(min=0, default=5, max=12)")

        conf['section_1.d'] = 13
        self.assertEqual(conf['section_1.d'], 13)
        conf.initialize(self.filename, spec=(
            [option.encode() for option in spec.split('\n')]))

        self.assertEqual(conf['section_1.d'], 5)

    def test_initialize_with_file_spec(self):
        """Test initializing uninitialized config with a file and spec
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5, max=12)")

        conf['section_1.a'] = 13
        self.assertEqual(conf['section_1.a'], 13)
        conf.initialize(self.filename, spec=(
            [option.encode() for option in spec.split('\n')]))

        self.assertEqual(conf['section_1.a'], 12)

    def test_load_conf(self):
        """Test loading a configuration
        """
        conf.load(self.filename)
        a_conf = conf['section_1.a']
        self.assertEqual(a_conf, '12')
        b_conf = conf['section_1.b']
        self.assertEqual(b_conf, '13')
        c_conf = conf['section_2.c']
        self.assertEqual(c_conf, 'True')

    def test_save_load_config(self):
        """Test saving and reloading conf
        """
        conf.load(self.filename)

        filename = tempfile.mkstemp()[1]
        conf.save(filename)

        # Destroy configuration
        conf.reset_instance()
        self.assertRaises(KeyError,
                          conf.__getitem__,
                          'section_1.a')

        conf.load(filename)
        a_conf = conf['section_1.a']
        self.assertEqual(a_conf, '12')
        b_conf = conf['section_1.b']
        self.assertEqual(b_conf, '13')
        c_conf = conf['section_2.c']
        self.assertEqual(c_conf, 'True')

        self.assertTrue(os.path.isfile(filename))
        # Clean up
        os.remove(filename)

    def test_len(self):
        """Test the length of the config is reported correctly
        """
        conf.load(self.filename)
        self.assertEqual(len(conf), 3)

    def test_set_value(self):
        """Test setting config values
        """
        conf.load(self.filename)
        self.assertFalse('a' in conf)
        conf['a'] = 2
        self.assertTrue('a' in conf)
        self.assertEqual(conf['a'], 2)

    def test_set_value_section(self):
        """Test setting config values in new section
        """
        conf.load(self.filename)
        self.assertFalse('a.b' in conf)
        conf['a.b'] = 2
        self.assertTrue('a.b' in conf)
        self.assertEqual(conf['a.b'], 2)

    def test_get_or_set(self):
        """Test get_or_setting config values
        """
        conf.load(self.filename)
        self.assertRaises(KeyError, conf.__getitem__, 'a')
        self.assertRaises(KeyError, conf.get, 'a')
        self.assertFalse('a' in conf)
        self.assertEqual(conf.get_or_set('a', 12), 12)
        self.assertEqual(conf.get('a'), 12)
        self.assertTrue('a' in conf)

    def test_keys(self):
        """Test the keys method on the configuration
        """
        self.assertEqual(list(conf.keys()), [])
        conf.load(self.filename)
        self.assertEqual(len(conf.keys()), 3)

    def test_override_with_args(self):
        """Test adding config options from dictionary
        """
        conf.load(self.filename)
        self.assertTrue('section_1.a' in conf)
        self.assertEqual(conf['section_1.a'], '12')
        conf.override_with_args([('section_1.a', '13')])
        self.assertEqual(conf['section_1.a'], '13')

    def test_override_with_args_level(self):
        """Test adding config options from dictionary at higher level
        """
        conf.load(self.filename)
        conf['section_1.section_12.a'] = '15'
        self.assertEqual(conf['section_1.section_12.a'], '15')
        conf.override_with_args([('section_1.section_12.a', '13')])
        self.assertEqual(conf['section_1.section_12.a'], '13')

    def test_override_with_args_level2(self):
        """Test adding config options from dictionary at new level
        """
        conf.load(self.filename)
        conf.override_with_args([('section_1.section_12.a', '13')])
        self.assertEqual(conf['section_1.section_12.a'], '13')

    def test_override_with_args_spec(self):
        """Test adding config options with a spec
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5, max=13)")

        conf.load(self.filename,
                  spec=(
                      [option.encode() for option in spec.split('\n')]))
        conf.override_with_args([('section_1.a', '13')])
        self.assertEqual(conf['section_1.a'], '13')
        conf.validate_config(conf.base)
        self.assertEqual(conf['section_1.a'], 13)

    def test_override_with_args_wrong(self):
        """Test adding config options with a wrong spec
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5, max=12)")
        expected_error = (
            r"Configuration does not adhere to the specification: "
            r"\[\(\['section_1'\], 'a', "
            r"VdtValueTooBigError\('the value \"13\" is too big.',\)\)\]")
        conf.load(self.filename,
                  spec=(
                      [option.encode() for option in spec.split('\n')]))
        conf.override_with_args([('section_1.a', '13')])
        self.assertRaisesRegexp(
            ValueError,
            expected_error,
            conf.validate_config,
            conf.base)

    def test_load_with_spec(self):
        """Test loading a configuration with a specification
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5)")
        conf.load(self.filename,
                  spec=(
                      [option.encode() for option in spec.split('\n')]))
        self.assertTrue('section_1.a' in conf)
        self.assertIsInstance(conf['section_1.a'], int)
        self.assertEqual(conf['section_1.a'], 12)

    def test_load_with_nested_spec(self):
        """Test loading a configuration with a nested specification
        """
        spec = ("[section_1]\n"
                "[[section_a]]\n"
                "a = integer(min=0, default=5)")
        conf.load(self.filename,
                  spec=(
                      [option.encode() for option in spec.split('\n')]))
        self.assertTrue('section_1.section_a.a' in conf)
        self.assertIsInstance(conf['section_1.section_a.a'], int)
        self.assertEqual(conf['section_1.section_a.a'], 5)

        self.assertTrue('section_1.a' in conf)
        self.assertIsInstance(conf['section_1.a'], str)
        self.assertEqual(conf['section_1.a'], '12')

    def test_load_with_wrong_spec(self):
        """Test loading a configuration that does not adhere to the specs
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5, max=7)")
        expected_error = (
            r"Configuration does not adhere to the specification: "
            r"\[\(\['section_1'\], 'a', "
            r"VdtValueTooBigError\('the value \"12\" is too big.',\)\)\]")

        self.assertRaisesRegexp(
            ValueError,
            expected_error,
            conf.load, self.filename, spec=(
                [option.encode() for option in spec.split('\n')]))
