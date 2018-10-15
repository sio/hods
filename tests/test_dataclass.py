'''
Unit tests for data classes
'''

from unittest import TestCase

from hods import (
    HashMismatchError,
    Metadata,
    TreeStructuredData as TSD,
    ValidationError,
)
from hods._lib.hash import struct_hash


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
        self.file = Metadata(filename='samples/sample-v1-02.json')

    def test_validation(self):
        with self.assertRaises(ValidationError):
            self.empty.hello = 1
        with self.assertRaises(ValidationError):
            self.file.data.hello = 1

    def test_hashes(self):
        meta = self.empty
        meta.validate_hashes()  # no-op, test if raises error
        meta.validate_hashes(write_updates=True)
        empty_hash = struct_hash({}, 'sha256')
        self.assertEqual(meta.info.hashes.data.sha256, empty_hash)
        meta.info.hashes.data.md5 = 'invalidhash'
        with self.assertRaises(HashMismatchError):
            meta.validate_hashes()

    def test_hash_for_new_section(self):
        meta = self.empty
        meta.validate_hashes(write_updates=True)

        new_section_contents = {'hello': 'world'}
        meta.new = new_section_contents
        meta.validate_hashes()  # no-op, check if everything is ok
        with self.assertRaises(AttributeError):
            meta.validate_hashes(sections=('new',))
        meta.validate_hashes(sections=('new',), write_updates=True)
        self.assertEqual(meta.info.hashes.new.md5, struct_hash(new_section_contents, 'md5'))
