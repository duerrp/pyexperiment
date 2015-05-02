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
import io

from pyexperiment.utils.stdout_redirector import stdout_redirector
from pyexperiment import conf


class TestConf(unittest.TestCase):
    """Test the conf module
    """
    TEST_CONFIG = ("[section_1]\n"
                   "a = 12\n"
                   "b = 13\n"
                   "[section_2]\n"
                   "c = True")

    def setUp(self):
        """Setup the test fixure
        """
        self.filename = tempfile.mkstemp()[1]
        with open(self.filename, 'w') as outfile:
            outfile.write(self.TEST_CONFIG)

    def tearDown(self):
        """Tear down the test fixure
        """
        conf.reset_instance()
        os.remove(self.filename)

    def test_uninitialized_conf(self):
        """Test uninitialized config throws Exception
        """
        conf.reset_instance()
        self.assertRaises(KeyError, conf.__getitem__, 'a')

    def test_load_conf(self):
        """Test loading a configuration
        """
        conf.load(self.filename, spec_filename="")
        a_conf = conf['section_1.a']
        self.assertEqual(a_conf, '12')
        b_conf = conf['section_1.b']
        self.assertEqual(b_conf, '13')
        c_conf = conf['section_2.c']
        self.assertEqual(c_conf, 'True')

    def test_save_no_config(self):
        """Test saving unititialized config
        """
        filename = tempfile.mkstemp()[1]
        self.assertRaises(RuntimeError, conf.save, filename)
        os.remove(filename)

    def test_save_config_wo_filename(self):
        """Test saving config without passing filename
        """
        buf = io.StringIO()
        conf.load(self.filename, spec_filename="")

        # Save should print something and return
        with stdout_redirector(buf):
            conf.save(None)

        self.assertNotEqual(len(buf.getvalue()), 0)

    def test_save_load_config(self):
        """Test saving and reloading conf
        """
        conf.load(self.filename, spec_filename="")

        filename = tempfile.mkstemp()[1]
        conf.save(filename)

        # Destroy configuration
        conf.reset_instance()
        self.assertRaises(KeyError,
                          conf.__getitem__,
                          'section_1.a')

        conf.load(filename, spec_filename="")
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
        conf.load(self.filename, spec_filename="")
        self.assertEqual(len(conf), 3)

    def test_in(self):
        """Test the `in` function works for config
        """
        conf.load(self.filename, spec_filename="")
        self.assertTrue('section_1.a' in conf)
        self.assertFalse('section_1.f' in conf)

    def test_get_default(self):
        """Test getting config values with a default argument
        """
        self.assertRaises(KeyError, conf.__getitem__, 'a')
        self.assertRaises(KeyError, conf.get, 'a')
        self.assertEqual(conf.get('a', default=12), 12)
        self.assertRaises(KeyError, conf.get, 'a')

    def test_set_value(self):
        """Test setting config values
        """
        conf.load(self.filename, spec_filename="")
        self.assertFalse('a' in conf)
        conf['a'] = 2
        self.assertTrue('a' in conf)
        self.assertEqual(conf['a'], 2)

    def test_set_value_section(self):
        """Test setting config values in new section
        """
        conf.load(self.filename, spec_filename="")
        self.assertFalse('a.b' in conf)
        conf['a.b'] = 2
        self.assertTrue('a.b' in conf)
        self.assertEqual(conf['a.b'], 2)

    def test_get_or_set(self):
        """Test get_or_setting config values
        """
        conf.load(self.filename, spec_filename="")
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
        conf.load(self.filename, spec_filename="")
        self.assertEqual(len(conf.keys()), 3)

    def test_override_with_args(self):
        """Test adding config options from dictionary
        """
        conf.load(self.filename, spec_filename="")
        self.assertTrue('section_1.a' in conf)
        self.assertEqual(conf['section_1.a'], '12')
        conf.override_with_args(conf.base, [('section_1.a', '13')])
        self.assertEqual(conf['section_1.a'], '13')

    def test_override_with_args_level(self):
        """Test adding config options from dictionary at higher level
        """
        conf.load(self.filename, spec_filename="")
        conf['section_1.section_12.a'] = '15'
        self.assertEqual(conf['section_1.section_12.a'], '15')
        conf.override_with_args(conf.base, [('section_1.section_12.a', '13')])
        self.assertEqual(conf['section_1.section_12.a'], '13')

    def test_override_with_args_level2(self):
        """Test adding config options from dictionary at new level
        """
        conf.load(self.filename, spec_filename="")
        conf.override_with_args(conf.base, [('section_1.section_12.a', '13')])
        self.assertEqual(conf['section_1.section_12.a'], '13')

    def test_load_with_spec(self):
        """Test loading a configuration with a specification
        """
        spec = ("[section_1]\n"
                "a = integer(min=0, default=5)")
        conf.load(self.filename,
                  spec_filename=(
                      [option.encode() for option in spec.split('\n')]))
        self.assertTrue('section_1.a' in conf)
        self.assertIsInstance(conf['section_1.a'], int)
        self.assertEqual(conf['section_1.a'], 12)

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
            conf.load, self.filename, spec_filename=(
                [option.encode() for option in spec.split('\n')]))
