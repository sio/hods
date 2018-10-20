'''
Unit tests for tag reader
'''


from unittest import TestCase

from hods.music.objects import MusicMetadata

class testReadTags(TestCase):

    def test_music(self):
        m = MusicMetadata()
        m.parse('/media/user/SANSA_SD/Maximo Park/2007 - Our Earthly Pleasures/')
        import pdb; pdb.set_trace()
