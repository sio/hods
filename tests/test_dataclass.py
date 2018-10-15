'''
Unit tests for data classes
'''

from unittest import TestCase

from hods import (
    Metadata,
    TreeStructuredData as TSD,
    ValidationError
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

    def test_new_branches(self):
        with self.assertRaises(AttributeError):
            self.data.tree = {'new': 'tree'}  # can not replace branches
        self.data.newtree = {'proper': 'new tree'}
        self.assertEqual(self.data.newtree.proper, 'new tree')
        self.assertEqual(self.data._data['newtree']['proper'], 'new tree')

    def test_equality(self):
        other = TSD(self.data._data)
        self.assertEqual(self.data, other)
        self.assertNotEqual(self.data._data, other)
        self.assertNotEqual('hello world', other)

    def test_dict_access(self):
        self.assertEqual(self.data.hello, self.data['hello'])
        self.data.tree.inner = 'new'
        self.assertEqual(self.data['tree']['inner'], 'new')
        self.data['tree']['inner'] = 'new2'
        self.assertEqual(self.data.tree.inner, 'new2')


class testMetadataHolder(TestCase):
    def setUp(self):
        self.empty = Metadata()
        self.file = Metadata(json_file='samples/sample-v1-02.json')

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.empty.hello = 1
        with self.assertRaises(ValidationError):
            self.file.data.hello = 1
