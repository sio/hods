'''
Reusable metadata objects for music files
'''


import os
import json
from collections import OrderedDict, defaultdict

from tinytag import TinyTag

from hods import Metadata


class MusicAlbumInfo(Metadata):
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


    def parse(self, dirname):
        '''Parse tags for all files in the directory (non-recursive'''
        album_info = OrderedDict((
            # MusicAlbumInfo field: TinyTag field
            ('album', 'album'),
            ('artist', 'albumartist'),
            ('year', 'year'),
            ('genre', 'genre'),
            ('cd', 'disc'),
            ('comment', 'comment'),
        ))
        track_info = OrderedDict((
            ('number', 'track'),
            ('title', 'title'),
            ('artist', 'artist'),
        ))

        basedir, _, files = next(os.walk(dirname))
        album_collected = defaultdict(set)
        tracks_collected = list()

        # Read information from music files
        for filename in sorted(files):
            filename = os.path.join(basedir, filename)
            if not TinyTag.is_supported(filename):
                continue
            tags = TinyTag.get(filename)
            for meta_attr, tag_attr in album_info.items():
                value = getattr(tags, tag_attr)
                if value and not isinstance(value, str):
                    value = value.pop()  # use first of multiple values
                if value:
                    album_collected[meta_attr].add(value)
            track = OrderedDict()
            for meta_attr, tag_attr in track_info.items():
                value = getattr(tags, tag_attr)
                if value and not isinstance(value, str):
                    value = value.pop()  # use first of multiple values
                if not value:
                    value = ''
                track[meta_attr] = value
            tracks_collected.append(track)

        # Analyze and extract information about the whole album
        for field, values in album_collected.items():
            if len(values) == 1:
                value = values.pop()
            elif len(values) == 0:
                value = ''
            elif len(values) > 1 and field in {'artist', 'comment'}:
                value = ', '.join(sorted(values))
            else:
                raise ValueError(
                    'unexpected multiple values for {}: {!r}'.format(
                        field,
                        tuple(values),
                    )
                )
            setattr(self.data, field, value)

        # Detect album artist
        if not self.data.artist:
            track_artists = set()
            for track in tracks_collected:
                track_artists.add(track['artist'])
            if len(track_artists) == 1:
                self.data.artist = track_artists.pop()

        # Do not write the same artist name into each track
        for track in tracks_collected:
            if track['artist'] == self.data.artist:
                track['artist'] = ''

        # Write the results
        self.data.tracks = sorted(tracks_collected, key=lambda x: x['number'])
        self.validate_hashes(write_updates=True)
