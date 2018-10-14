'''
Classes for accessing and manipulating structured data
'''


import json
import os.path
from collections.abc import Mapping

import jsonschema

from datahash import datahash


class TreeStructuredData:
    '''
    Generic data class. Keeps all data in one tree-like object and exposes its
    nodes via attributes. Child objects refer to the same data tree as the
    parent.

    Handles reading, modification and validation of data structure.
    '''
    __slots__ = (
        '_data',
        '_children',
        '_parent',
        '_validator',
    )


    def __init__(self, data, parent=None, validator=None):
        if not is_mapping(data):
            raise ValueError(
                "{cls}() expected a mapping object but received '{data}'".format(
                    cls = type(self).__name__,
                    data = type(data).__name__,
                )
            )
        self._data = data
        self._parent = parent
        self._children = dict()
        self._validator = validator
        self.validate()


    def validate(self):
        '''
        Ensure this data tree and its parent are valid, raise ValidationError
        otherwise.
        '''
        if self._validator is not None:
            self._validator(self._data)
        if self._parent is not None:
            self._parent.validate()


    def __getattr__(self, attr):
        if attr in self._children:
            response = self._children[attr]
        elif attr in self._data:
            if is_mapping(self._data[attr]):
                response = self._children[attr] = \
                    type(self)(data=self._data[attr], parent=self)
            else:
                response = self._data[attr]
        else:
            raise AttributeError(
                "'{cls}' object has no attribute '{attr}'".format(
                    cls=self.__class__.__name__,
                    attr=attr
                )
            )
        return response


    def __setattr__(self, attr, value):
        reserved = set(self.__slots__)

        node_exists = attr not in reserved and attr in self._data
        node_is_mapping = node_exists and is_mapping(self._data[attr])
        value_is_mapping = node_exists and is_mapping(value)

        if attr in reserved \
        or (hasattr(self, attr) and not node_exists):  # not a data point
            return super().__setattr__(attr, value)

        if (node_exists and not node_is_mapping and not value_is_mapping) \
        or not node_exists:
            self._data[attr] = value  # write leaf/branch value
            self.validate()
        elif node_exists and node_is_mapping and not value_is_mapping:
            raise AttributeError('can not replace branch node with leaf node: {}'.format(attr))
        elif node_exists and not node_is_mapping and value_is_mapping:
            raise AttributeError('can not replace leaf node with branch node: {}'.format(attr))
        elif node_exists and node_is_mapping and value_is_mapping:
            raise AttributeError('can not replace existing branch with another: {}'.format(attr))
        else:
            raise RuntimeError('this branching should not be possible')


    def __repr__(self):
        return '<{cls}({data}{parent})>'.format(
            cls = self.__class__.__name__,
            data = self._data,
            parent = ', <child of #%s>' % id(self._parent) if self._parent else ''
        )


    def __eq__(self, other):
        if isinstance(other, type(self)):
            return datahash(self) == datahash(other)
        else:
            return NotImplemented

    def __iter__(self):
        return iter(self._data)


class Metadata:
    '''
    Holds structured data with a defined schema.

    Validates data against the schema after each change. Calculates hashes of
    data values.
    '''
    _INITIAL = '''
        {
            "info": {
                "version": "metadata-v1.json",
                "schema": {
                    "data": ""
                },
                "hashes": {
                    "data": {
                        "timestamp": "0000-00-00T00:00:00+00:00"
                    }
                }
            },
            "data": {}
        }
    '''

    __slots__ = (
        '_data_container',
    )

    def __init__(self, data=None, json_file=None, yaml_file=None):
        if data is None:
            if json_file is not None:
                with open(json_file) as f:
                    data = json.load(f)
            elif yaml_file is not None:
                raise NotImplementedError  # TODO
            else:
                data = json.loads(self._INITIAL)

        schema = get_schema(data['info']['version'])
        self._data_container = TreeStructuredData(data, validator=validator(schema))

        for key in self.info.schema:
            branch = getattr(self, key)
            schema = get_schema(getattr(self.info.schema, key))
            branch._validator = validator(schema)

    def __getattr__(self, attr):
        return getattr(self._data_container, attr)

    def __setattr__(self, attr, value):
        try:
            self.__getattribute__(attr)
            use_container = False
        except AttributeError:
            use_container = attr not in self.__slots__

        if use_container:
            setattr(self._data_container, attr, value)
        else:
            super().__setattr__(attr, value)

    def __iter__(self):
        return iter(self._data_container)

    def __repr__(self):
        return '<{cls} object (schema={schema}, id={id})>'.format(
            cls = self.__class__.__name__,
            schema = self.info.version,
            id = id(self),
        )


class TranslatorWrapper:
    '''
    Helper class to simplify class composition and wrapping properties

    THIS IS NOT NECESSARY. SIMPLY DEFINE REQUIRED METHODS AND PROPERTIES IN
    AlbumMetadata
    '''
    pass



class AlbumMetadata:
    '''
    Stable API for music album metadata
    '''
    pass



def is_mapping(value):
    '''Check if argument value is mapping'''
    return isinstance(value, Mapping)


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
        schema_filename = os.path.join('schemas', identificator)
        with open(schema_filename) as f:
            return json.load(f)
    else:
        raise ValueError('unknown schema engine: {}'.format(engine))
