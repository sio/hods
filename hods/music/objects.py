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
    _SUPPORTED_SCHEMAS = [  # first one is used for creating empty objects
        'https://hods.ml/schemas/music-album-v1.json',
    ]
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
            data['info']['schema']['data'] = self._SUPPORTED_SCHEMAS[0]

        super().__init__(data, filename, fileformat)

        schema = self.info.schema.data
        if schema not in self._SUPPORTED_SCHEMAS:
            raise ValueError('schema is not supported: {}'.format(schema))
