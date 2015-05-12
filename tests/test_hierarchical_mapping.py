"""Test the HierarchicalMapping base class

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest

from pyexperiment.utils.HierarchicalMapping import HierarchicalOrderedDict
from pyexperiment.utils.HierarchicalMapping import HierarchicalDict


class TestHierarchicalOrderedDict(unittest.TestCase):
    """Test the ``HierarchicalOrderedDict``
    """
    def setUp(self):
        """Set up the test fixture
        """
        self.hod = HierarchicalOrderedDict()

    def test_len_empty_mapping(self):
        """Test if the empty mapping is really empty
        """
        self.assertEqual(len(self.hod), 0)

    def test_insert_retrieve_base_level(self):
        """Make sure we can use the container at the base
        """
        self.hod['a'] = 12

        self.assertEqual(self.hod['a'], 12)

    def test_retrieve_second_level(self):
        """Make sure we can use the container at the second level
        """
        self.hod['hello.world'] = 12
        self.assertEqual(self.hod['hello.world'], 12)

    def test_len_after_first_level(self):
        """Test if the length is correct after inserting at the first level
        """
        self.assertEqual(len(self.hod), 0)

        # New keys should increase the length
        for i, key in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
            self.hod[key] = i ** 2
            self.assertEqual(len(self.hod), i + 1)

        # Existing keys should keep the length
        for key in ['a', 'b', 'c', 'd', 'e', 'f']:
            self.hod[key] = 12
            self.assertEqual(len(self.hod), 5 + 1)

    def test_inserting_higher_levels(self):
        """Test if the length is correct after inserting at the first level
        """
        self.assertEqual(len(self.hod), 0)

        # New keys should increase the length
        i = 0
        for key1 in ['a', 'b', 'c', 'd', 'e', 'f']:
            for key2 in ['a', 'b', 'c', 'd', 'e', 'f']:
                i += 1
                self.hod[key1 + '.' + key2] = i
                self.assertEqual(len(self.hod), i)

    def test_keys(self):
        """Test the keys method on the mapping
        """
        self.assertEqual(len(self.hod), 0)

        # New keys
        keys = ['a', 'b', 'c', 'd', 'e', 'f']
        for i, key in enumerate(keys):
            self.hod[key] = i
        self.assertEqual(list(self.hod.keys()), keys)

    def test_contains(self):
        """Test the HierarchicalOrderedDict with `in`
        """
        self.assertEqual(len(self.hod), 0)

        self.assertFalse('a' in self.hod)
        self.hod['a'] = 1
        self.assertTrue('a' in self.hod)

        self.assertFalse('b.c.d' in self.hod)
        self.hod['b.c.d'] = 1
        self.assertTrue('b.c.d' in self.hod)

    def test_get(self):
        """Test getting values with and without default values
        """
        self.assertRaises(KeyError, self.hod.get, 'a')
        self.assertEqual(self.hod.get('a', 42), 42)
        self.hod['a'] = 123
        self.assertEqual(self.hod.get('a', 42), 123)

    def test_get_or_set(self):
        """Test get_or_setting values
        """
        self.hod = HierarchicalOrderedDict()
        self.assertRaises(KeyError, self.hod.get, 'a')
        self.assertEqual(self.hod.get_or_set('a', 42), 42)
        self.assertEqual(self.hod.get('a'), 42)
        self.hod['a'] = 52
        self.assertEqual(self.hod.get_or_set('a', 42), 52)

    def test_base_keys(self):
        """Test getting the base keys
        """
        self.hod = HierarchicalOrderedDict()
        self.hod['a'] = 12
        self.hod['b'] = 13
        self.hod['c.d'] = 14
        self.hod['e.f.g'] = 15

        base_keys = self.hod.base_keys()
        self.assertIn('a', base_keys)
        self.assertIn('b', base_keys)
        self.assertIn('c', base_keys)
        self.assertIn('e', base_keys)
        self.assertNotIn('c.d', base_keys)
        self.assertNotIn('d', base_keys)
        self.assertNotIn('e.f', base_keys)
        self.assertNotIn('e.f.g', base_keys)
        self.assertNotIn('f.g', base_keys)
        self.assertNotIn('f', base_keys)
        self.assertNotIn('g', base_keys)

    def test_merge_empty(self):
        """Test merging in empty mapping
        """
        self.hod = HierarchicalOrderedDict()
        self.hod['a'] = 12
        self.hod['b'] = 13
        self.hod['c.d'] = 14
        self.hod['e.f.g'] = 15
        items = list(self.hod.items())

        m_2 = HierarchicalOrderedDict()
        self.hod.merge(m_2)
        self.assertEqual(len(self.hod), 4)
        for key, value in items:
            self.hod[key] = value

    def test_merge_same(self):
        """Test merging mapping with same keys
        """
        self.hod = HierarchicalOrderedDict()
        self.hod['a'] = 12
        self.hod['b'] = 13
        self.hod['c.d'] = 14
        self.hod['e.f.g'] = 15
        items = list(self.hod.items())

        m_2 = HierarchicalOrderedDict()
        m_2['a'] = 12
        m_2['b'] = 13
        m_2['c.d'] = 14
        m_2['e.f.g'] = 15
        self.hod.merge(m_2)
        self.assertEqual(len(self.hod), 4)
        for key, value in items:
            self.hod[key] = value

    def test_merge_other_keys(self):
        """Test merging in mapping with other keys
        """
        self.hod = HierarchicalOrderedDict()
        self.hod['a'] = 12
        self.hod['b'] = 13
        self.hod['c.d'] = 14
        self.hod['e.f.g'] = 15
        items = list(self.hod.items())

        m_2 = HierarchicalOrderedDict()
        m_2['k'] = 13
        m_2['l.m.n'] = 'bla'
        items2 = list(m_2.items())

        self.hod.merge(m_2)

        self.assertEqual(len(self.hod), 6)
        for key, value in items + items2:
            self.hod[key] = value

    def test_merge_overlapping(self):
        """Test merging in mapping with overlapping keys
        """
        self.hod['a'] = 12
        self.hod['b'] = 13
        self.hod['c.d'] = 14
        self.hod['e.f.g'] = 15
        items = list(self.hod.items())

        m_2 = HierarchicalOrderedDict()
        m_2['c.d'] = 10
        m_2['k'] = 13
        m_2['l.m.n'] = 'bla'
        items2 = list(m_2.items())

        self.hod.merge(m_2)

        self.assertEqual(len(self.hod), 6)
        for key, value in items:
            self.hod[key] = value
        for key, value in items2:
            if key not in [item[0] for item in items]:
                self.hod[key] = value

    def test_section_keys(self):
        """Test the section_keys method on the mapping
        """
        self.assertEqual(len(list(self.hod.section_keys())), 0)

        # New keys
        keys = ['a', 'b.c', 'd.e.f', 'g.h', 'j.k.l.m']
        for i, key in enumerate(keys):
            self.hod[key] = i

        self.assertIn('b', self.hod.section_keys())
        self.assertIn('d.e', self.hod.section_keys())
        self.assertIn('g', self.hod.section_keys())
        self.assertIn('j.k.l', self.hod.section_keys())
        self.assertNotIn('a', self.hod.section_keys())
        self.assertNotIn('c', self.hod.section_keys())
        self.assertNotIn('b.c', self.hod.section_keys())
        self.assertNotIn('e', self.hod.section_keys())
        self.assertNotIn('e.f', self.hod.section_keys())
        self.assertNotIn('d.e.f', self.hod.section_keys())
        self.assertNotIn('h', self.hod.section_keys())
        self.assertNotIn('m', self.hod.section_keys())


class TestHierarchicalDict(unittest.TestCase):
    """Test the ``HierarchicalMapping`` based on ``dict``.
    """
    def setUp(self):
        """Set up the fixture
        """
        self.hdict = HierarchicalDict()

    def test_len(self):
        """Test the ``HierarchicalDict``'s len method
        """
        self.assertEqual(len(self.hdict), 0)

        self.hdict['a.b.c'] = 3
        self.assertEqual(len(self.hdict), 1)

        self.hdict['d'] = 4
        self.assertEqual(len(self.hdict), 2)

        del self.hdict['d']
        self.assertEqual(len(self.hdict), 1)

    def test_insert_retrieve(self):
        """Test inserting and retrieving element of ``HierarchicalDict``
        """
        self.hdict['a.b.c'] = 12
        self.assertEqual(self.hdict['a.b.c'], 12)


if __name__ == '__main__':
    unittest.main()
