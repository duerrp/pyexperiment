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
