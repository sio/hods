'''
Reusable metadata objects for music files
'''


import json
from collections import OrderedDict

from hods import Metadata


class MusicMetadata(Metadata):
    '''
    Manipulate music metadata with HODS
    '''
    _EMPTY_JSON = '''
        {
          "album": "...",
          "artist": "",
          "year": "0000",
          "image_url": "",
          "genre": "",
          "comment": "",
          "composer": "",
          "orig_artist": "",
          "cd": "",
          "tracks": []
        }
    '''

    def __init__(self, data=None, filename=None, fileformat=None):
        if data is None and filename is None:
            load = lambda x: json.loads(x, object_pairs_hook=OrderedDict)
            payload = load(self._EMPTY_JSON)
            data = load(Metadata._EMPTY_JSON)
            data['data'] = payload
            data['info']['schema']['data'] = 'https://hods.ml/schemas/music-album-v1.json'
        super().__init__(data, filename, fileformat)
