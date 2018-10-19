'''
Unit tests for music metadata objects
'''


from unittest import TestCase

from hods import ValidationErrors
from hods.music.objects import MusicMetadata
from hods._lib.core import TranslatorWrapper


class testMusicMetadata(TestCase):

    def test_empty_init(self):
        m = MusicMetadata()

    def test_payload_validation(self):
        m = MusicMetadata()
        with self.assertRaises(ValidationErrors):
            m['disallowed key'] = 1
        with self.assertRaises(ValidationErrors):
            m.album = ''  # defined as non-empty in schema

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
