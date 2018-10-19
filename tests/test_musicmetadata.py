'''
Unit tests for music metadata objects
'''


from unittest import TestCase

from hods import ValidationErrors
from hods.music.objects import MusicMetadata


class testMusicMetadata(TestCase):

    def test_empty_init(self):
        m = MusicMetadata()

    def test_payload_validation(self):
        m = MusicMetadata()
        with self.assertRaises(ValidationErrors):
            m['disallowed key'] = 1
        with self.assertRaises(ValidationErrors):
            m.album = ''  # defined as non-empty in schema
