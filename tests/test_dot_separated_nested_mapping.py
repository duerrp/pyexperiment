"""Test the DotSeparatedNestedMapping base class
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import unittest
from collections import OrderedDict

from pyexperiment.utils.DotSeparatedNestedMapping \
    import DotSeparatedNestedMapping


class TestDotSeparatedNestedMapping(unittest.TestCase):
    """Test the DotSeparatedNestedMapping
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
        m = DotSeparatedNestedMapping(OrderedDict)
        self.assertEqual(len(m), 0)

    def test_insert_retrieve_base_level(self):
        """Make sure we can use the container at the base
        """
        m = DotSeparatedNestedMapping(OrderedDict)
        m['a'] = 12

        self.assertEqual(m['a'], 12)

    def test_retrieve_second_level(self):
        """Make sure we can use the container at the second level
        """
        m = DotSeparatedNestedMapping(OrderedDict)
        m['hello.world'] = 12
        self.assertEqual(m['hello.world'], 12)

    def test_len_after_inserting_at_first_level(self):
        """Test if the length is correct after inserting at the first level
        """
        m = DotSeparatedNestedMapping(OrderedDict)
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
        m = DotSeparatedNestedMapping(OrderedDict)
        self.assertEqual(len(m), 0)

        # New keys should increase the length
        i = 0
        for key1 in ['a', 'b', 'c', 'd', 'e', 'f']:
            for key2 in ['a', 'b', 'c', 'd', 'e', 'f']:
                i += 1
                m[key1 + '.' + key2] = i
                self.assertEqual(len(m), i)


if __name__ == '__main__':
    unittest.main()
