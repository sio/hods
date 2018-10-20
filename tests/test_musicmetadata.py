'''
Unit tests for music metadata objects
'''


from unittest import TestCase

from hods import ValidationErrors
from hods.music.objects import MusicAlbumInfo
from hods._lib.core import TranslatorWrapper


class testMusicAlbumInfo(TestCase):

    def test_empty_init(self):
        m = MusicAlbumInfo()

    def test_payload_validation(self):
        m = MusicAlbumInfo()
        with self.assertRaises(ValidationErrors):
            m['disallowed key'] = 1
        with self.assertRaises(ValidationErrors):
            m.album = ''  # defined as non-empty in schema

    def test_unsupported_schema(self):
        with self.assertRaises(ValueError):
            MusicAlbumInfo(filename='tests/data/samples/sample-v1-02.json')

class Temp:
    pass

class testAttributeTranslation(TestCase):

    def test_translation(self):
        base = Temp()
        base.hello = 123
        m = TranslatorWrapper(base)
        m._wrap = {'test': 'hello'}
        self.assertEqual(m.test, 123)
        m.test = 321
        self.assertEqual(base.hello, 321)
