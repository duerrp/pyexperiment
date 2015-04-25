"""Test the HierarchicalMapping base class
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest

from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalMapping

from pyexperiment.utils.HierarchicalMapping \
    import HierarchicalOrderedDict


class TestHierarchicalMapping(unittest.TestCase):
    """Test the HierarchicalMapping
    """
    def setUp(self):
        """Setup the test fixure
        """
        pass

    def tearDown(self):
        """Tear down the test fixure
        """
        pass

    def test_len_empty_mapping(self):
        """Test if the empty mapping is really empty
        """
        m = HierarchicalOrderedDict()
        self.assertEqual(len(m), 0)

    def test_insert_retrieve_base_level(self):
        """Make sure we can use the container at the base
        """
        m = HierarchicalOrderedDict()
        m['a'] = 12

        self.assertEqual(m['a'], 12)

    def test_retrieve_second_level(self):
        """Make sure we can use the container at the second level
        """
        m = HierarchicalOrderedDict()
        m['hello.world'] = 12
        self.assertEqual(m['hello.world'], 12)

    def test_len_after_inserting_at_first_level(self):
        """Test if the length is correct after inserting at the first level
        """
        m = HierarchicalOrderedDict()
        self.assertEqual(len(m), 0)

        # New keys should increase the length
        for i, key in enumerate(['a', 'b', 'c', 'd', 'e', 'f']):
            m[key] = 1
            self.assertEqual(len(m), i + 1)

        # Existing keys should keep the length
        for key in ['a', 'b', 'c', 'd', 'e', 'f']:
            m[key] = 1
            self.assertEqual(len(m), 5 + 1)

    def test_inserting_higher_levels(self):
        """Test if the length is correct after inserting at the first level
        """
        m = HierarchicalOrderedDict()
        self.assertEqual(len(m), 0)

        # New keys should increase the length
        i = 0
        for key1 in ['a', 'b', 'c', 'd', 'e', 'f']:
            for key2 in ['a', 'b', 'c', 'd', 'e', 'f']:
                i += 1
                m[key1 + '.' + key2] = i
                self.assertEqual(len(m), i)

    def test_keys(self):
        """Test the keys method on the mapping
        """
        m = HierarchicalOrderedDict()
        self.assertEqual(len(m), 0)

        # New keys
        keys = ['a', 'b', 'c', 'd', 'e', 'f']
        for i, key in enumerate(keys):
            m[key] = i
        self.assertEqual(list(m.keys()), keys)

    def test_contains(self):
        """Test the HierarchicalOrderedDict with `in`
        """
        m = HierarchicalOrderedDict()
        self.assertEqual(len(m), 0)

        self.assertFalse('a' in m)
        m['a'] = 1
        self.assertTrue('a' in m)

        self.assertFalse('b.c.d' in m)
        m['b.c.d'] = 1
        self.assertTrue('b.c.d' in m)

    def test_other_base(self):
        """Test the HierarchicalOrderedDict with another base
        """
        class DotSeparatedDict(  # pylint: disable=too-many-ancestors
                HierarchicalMapping):
            """Example instance of the HierarchicalMapping
            """
            @classmethod
            def _new_section(cls):
                """Creates a new section Mapping
                """
                return dict()

            @classmethod
            def _is_section(cls, obj):
                """Returns true if obj is a section
                """
                return isinstance(obj, dict)

            def __init__(self):
                """Initializer
                """
                super(DotSeparatedDict, self).__init__()
                self.base = dict()

        m = DotSeparatedDict()
        m['a.b.c'] = 3
        self.assertEqual(len(m), 1)
        self.assertEqual(m['a.b.c'], 3)

    def test_get(self):
        """Test getting values with and without default values
        """
        m = HierarchicalOrderedDict()
        self.assertRaises(KeyError, m.get, 'a')
        self.assertEqual(m.get('a', 42), 42)
        m['a'] = 123
        self.assertEqual(m.get('a', 42), 123)

    def test_get_or_set(self):
        """Test get_or_setting values
        """
        m = HierarchicalOrderedDict()
        self.assertRaises(KeyError, m.get, 'a')
        self.assertEqual(m.get_or_set('a', 42), 42)
        self.assertEqual(m.get('a'), 42)
        m['a'] = 52
        self.assertEqual(m.get_or_set('a', 42), 52)

if __name__ == '__main__':
    unittest.main()
