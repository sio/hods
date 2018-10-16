'''
Classes for accessing and manipulating structured data
'''


import json
import os.path
import shutil
from collections import namedtuple
from collections.abc import Mapping
from datetime import datetime, timezone

import jsonschema

from hods import (
    HashMismatchError,
    __name__ as _top_level_module,
)
from hods._lib.hash import datahash
from hods._lib.files import (
    detect_format,
    get_object,
    write_object,
)


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
    __module__ = _top_level_module


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


    def __getitem__(self, key):
        '''Fallback dictionary API. Use attribute access as the primary API'''
        return self.__getattr__(key)


    def __setitem__(self, key, value):
        '''Fallback dictionary API. Use attribute access as the primary API'''
        return self.__setattr__(key, value)



class Metadata:
    '''
    Holds structured data with a defined schema.

    Validates data against the schema after each change. Calculates hashes of
    data values.
    '''
    __slots__ = (
        '_data_container',
        '_file',
    )
    __module__ = _top_level_module


    def __init__(self, data=None, filename=None, fileformat=None):
        if filename or fileformat:
            self._file = FileInfo(filename, fileformat)
        else:
            self._file = None

        if data is None:
            if filename is not None:
                data = get_object(filename, fileformat)
            else:
                data = json.loads(EMPTY_METADATA_INIT)

        schema = get_schema(data['info']['version'])
        self._data_container = TreeStructuredData(data, validator=validator(schema))

        for key in self.info.schema:
            branch = getattr(self, key)
            schema = get_schema(getattr(self.info.schema, key))
            branch._validator = validator(schema)


    def write(self, filename=None, fileformat=None, backup='.hods~'):
        '''Write changed data structure into the file'''

        self.validate_hashes()  # TODO: maybe update hashes implicitly?

        if filename:
            if not fileformat: fileformat = detect_format(filename)
        else:
            filename, fileformat = self._file

        if not filename:
            raise ValueError('can not write data without filename')

        if backup:  # create backup file with given suffix
            try:
                shutil.copyfile(filename, filename + backup)
                backup_created = True
            except FileNotFoundError:  # for writing to new files
                backup_created = False

        write_object(self._data, filename, fileformat)

        if backup and backup_created:  # if no errors occured, remove backup file
            os.remove(filename + backup)


    def validate_hashes(self, write_updates=False, sections=(), required=('md5', 'sha256')):
        '''Check validity of data hashes and write updated values if neccessary'''
        if not sections:
            sections = set(self.info.hashes)
        for section in sections:
            try:
                hashes = self.info.hashes[section]
            except AttributeError:
                if write_updates:
                    self.info.hashes[section] = {'timestamp': timestamp()}
                hashes = self.info.hashes[section]

            data = self[section]
            algorithms = set(hashes).union(required)

            for algo in algorithms:
                if algo == 'timestamp':
                    continue
                try:
                    current = hashes[algo]
                except AttributeError:
                    current = None
                actual = datahash(data, algo)

                if current == actual or (not write_updates and current is None):
                    continue
                elif write_updates:
                    hashes[algo] = actual
                    hashes.timestamp = timestamp()
                else:
                    raise HashMismatchError(
                        '{algo} hash for {section} is {actual}, not {current}'.format(**locals())
                    )


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


    def __getitem__(self, key):
        '''Fallback dictionary API. Use attribute access as the primary API'''
        return self._data_container.__getitem__(key)


    def __setitem__(self, key, value):
        '''Fallback dictionary API. Use attribute access as the primary API'''
        return self._data_container.__setitem__(key, value)



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
        return get_object(schema_filename, fileformat='JSON')
    else:
        raise ValueError('unknown schema engine: {}'.format(engine))


def timestamp():
    offset = (
        datetime.now().replace(microsecond=0)
        - datetime.utcnow().replace(microsecond=0)
    )
    return datetime.now(timezone(offset)).replace(microsecond=0).isoformat()


FileInfo = namedtuple('FileInfo', 'name,format')


EMPTY_METADATA_INIT = '''
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
