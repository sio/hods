'''
Helpers for working with data schemas
'''


import os
import jsonschema

from hods._lib.files import (
    get_object,
)


class Schema:
    '''
    Wrapper class with stable API for validating data with different schema
    engines
    '''
    __slots__ = (
        'parsed',
        'engine',
        'id',
    )


    def __init__(self, identifier, engine='jsonschema'):
        '''Get schema object by schema ID (usually URL)'''
        # TODO:
        #   - Fetch schema from URL
        #   - Fetch schema from package contents
        #   - Detect known URLs and get them from package instead of URL
        #   - Use package contents for schemas without path
        #   - Define fallback URL prefix for schemas without path
        self.id = identifier
        self.engine = engine

        if not identifier:
            self.parsed = None
        elif engine == 'jsonschema':
            schema_filename = os.path.join('hods', 'schemas', identifier)
            self.parsed = get_object(schema_filename, fileformat='JSON')
        else:
            raise ValueError('unknown schema engine: {}'.format(engine))


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
