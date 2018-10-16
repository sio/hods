'''
Helpers for working with data schemas
'''


import os
import json
import jsonschema
import urllib
import pkg_resources
from collections import OrderedDict
from functools import lru_cache


URL_PREFIXES_MIRRORED_IN_PACKAGE = OrderedDict((
    # The first entry is used as default prefix for relative paths
    ('https://raw.githubusercontent.com/sio/hods/master/hods/schemas/', 'schemas/'),
))


class Schema:
    '''
    Wrapper class with stable API for validating data with different schema
    engines
    '''
    __slots__ = (
        'parsed',
        'engine',
        'id',
        'raw',
    )


    def __init__(self, identifier=None, engine='jsonschema'):
        '''Get schema object by schema ID (usually URL)'''
        if not identifier:  # Allow empty schema
            self.parsed = None
            self.engine = engine
            self.id = None
            self.raw = None
            return

        identifier = restore_full_schema_id(identifier)
        local_path = get_package_path(identifier)
        raw_schema = None
        if local_path:
            try:
                raw_schema = read_from_package(local_path)
            except FileNotFoundError:
                pass
        if not raw_schema:
            raw_schema = read_from_url(identifier)

        if engine == 'jsonschema':
            self.parsed = json.loads(raw_schema)
        else:
            raise ValueError('unknown schema engine: {}'.format(engine))

        self.id = identifier
        self.engine = engine
        self.raw = raw_schema


    def validate(self, data):
        '''
        Validate native Python data structure against the schema.

        Raises `hods.ValidationError` for invalid data.
        '''
        if self.parsed is None:
            return
        if self.engine == 'jsonschema':
            return jsonschema.validate(data, self.parsed)
        else:
            raise ValueError('unknown schema engine: {}'.format(self.engine))


    def __repr__(self):
        return 'Schema(identifier={!r}, engine={!r})'.format(self.id, self.engine)



def detect_schema_engine(identifier):  # TODO
    pass


def read_from_package(path):
    '''Get contents of a file in this package'''
    package = 'hods'
    return pkg_resources.resource_string(package, path).decode()


@lru_cache(maxsize=32)
def read_from_url(url):
    '''Get text contents from remote URL'''
    with urllib.request.urlopen(url) as response:
        try:
            encoding = response.headers.get_content_charset()
        except Exception:
            encoding = 'utf-8'
        return response.read().decode(encoding)


def get_package_path(url):
    '''
    Detect schemas available from Python package to avoid hitting network for
    locally available content
    '''
    for prefix, directory in URL_PREFIXES_MIRRORED_IN_PACKAGE.items():
        if url.startswith(prefix):
            return url.replace(prefix, directory)


def restore_full_schema_id(partial):
    '''
    Turn schema filename without path into full URL
    '''
    default_prefix = next(iter(URL_PREFIXES_MIRRORED_IN_PACKAGE))
    if '/' not in partial:
        return urllib.parse.urljoin(default_prefix, partial)
    else:
        return partial
