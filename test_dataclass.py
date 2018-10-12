'''
Unit tests for data classes
'''

from unittest import TestCase

from jsonschema.exceptions import ValidationError

from dataclass import (
    TreeStructuredData as TSD,
    Metadata,
)


class testTreeWrapper(TestCase):

    def setUp(self):
        sample = {
            'hello': 'world',
            'tree': {
                'inner': 'value',
                'second': {
                    'level': 'of nesting',
                },
                'list': [1,2,3,4],
                'tuple': (5,6,7),
            },
        }
        self.data = TSD(sample)

    def test_nesting(self):
        data = self.data
        self.assertEqual(data.hello, 'world')
        self.assertEqual(data.tree.inner, 'value')
        self.assertEqual(data.tree.second.level, 'of nesting')
        self.assertFalse(hasattr(data.tree, 'nonexistent'))

    def test_newbranches(self):
        with self.assertRaises(AttributeError):
            self.data.tree = {'new': 'tree'}  # can not replace branches
        self.data.newtree = {'proper': 'new tree'}
        self.assertEqual(self.data.newtree.proper, 'new tree')
        self.assertEqual(self.data._data['newtree']['proper'], 'new tree')


class testMetadataHolder(TestCase):
    def setUp(self):
        self.empty = Metadata()

    def test_empty_object(self):
        meta = self.empty
        with self.assertRaises(ValidationError):
            meta.hello = 1
