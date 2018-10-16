'''
Helpers for working with data schemas
'''


import os
import jsonschema
from hods._lib.files import (
    get_object,
)


def validator(schema, engine='jsonschema'):
    '''Factory for creating validator functions'''
    def validate(data):
        if schema is None:
            return
        if engine == 'jsonschema':
            return jsonschema.validate(data, schema)
        else:
            raise ValueError('unknown schema engine: {}'.format(engine))
    return validate


def get_schema(identificator, engine='jsonschema'):
    '''Get schema object by schema ID (usually URL)'''
    # TODO:
    #   - Fetch schema from URL
    #   - Fetch schema from package contents
    #   - Detect known URLs and get them from package instead of URL
    #   - Use package contents for schemas without path
    #   - Define fallback URL prefix for schemas without path
    if not identificator:
        return None
    if engine == 'jsonschema':
        schema_filename = os.path.join('hods', 'schemas', identificator)
        return get_object(schema_filename, fileformat='JSON')
    else:
        raise ValueError('unknown schema engine: {}'.format(engine))
