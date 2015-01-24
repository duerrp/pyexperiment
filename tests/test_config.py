"""Tests the conf module of pyexperiment

Written by Peter Duerr
"""

import unittest
import tempfile
import os
from pyexperiment.conf import conf


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
        os.remove(self.filename)

    def test_uninitialized_conf(self):
        """Test uninitialized config throws Exception
        """
        conf.Config().get_instance().config = None
        self.assertRaises(RuntimeError, conf.get_value, 'a')

    def test_load_conf(self):
        """Test loading a configuration
        """
        conf.load(self.filename, spec_filename="")
        a = conf.get_value('section_1.a')
        self.assertEqual(a, '12')
        b = conf.get_value('section_1.b')
        self.assertEqual(b, '13')
        c = conf.get_value('section_2.c')
        self.assertEqual(c, 'True')

    def test_save_conf_creates_file(self):
        """Test saving a configuration really creates a file
        """
        conf.load(self.filename, spec_filename="")

        filename = tempfile.mkstemp()[1]
        conf.save(filename)

        self.assertTrue(os.path.isfile(filename))
        # Clean up
        os.remove(filename)

    def test_save_load_config(self):
        """Test saving and reloading conf
        """
        conf.load(self.filename, spec_filename="")

        filename = tempfile.mkstemp()[1]
        conf.save(filename)

        # Destroy configuration
        conf.Config.get_instance().config = None
        self.assertRaises(RuntimeError,
                          conf.get_value,
                          'section_1.a')

        conf.load(filename, spec_filename="")
        a = conf.get_value('section_1.a')
        self.assertEqual(a, '12')
        b = conf.get_value('section_1.b')
        self.assertEqual(b, '13')
        c = conf.get_value('section_2.c')
        self.assertEqual(c, 'True')

        self.assertTrue(os.path.isfile(filename))
        # Clean up
        os.remove(filename)
