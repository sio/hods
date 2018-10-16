'''
File operations for HODS

Supported file formats:
    - StrictYAML - YAML files with .syml extension
    - JSON - .json extension
'''


import os
import json
from collections import OrderedDict
import strictyaml


def get_object(filename, fileformat=None):
    '''Read serialized object from file. Detect file format if not specified'''
    if not fileformat:
        fileformat = detect_format(filename)
    loaders = {
        'JSON':       load_json,
        'StrictYAML': load_strict_yaml,
    }
    return loaders[fileformat](filename)


def write_object(obj, filename, fileformat=None):
    '''Write serialized object to file. Detect file format if not specified'''
    if not fileformat:
        fileformat = detect_format(filename)
    writers = {
        'JSON':       write_json,
        'StrictYAML': write_strict_yaml,
    }
    return writers[fileformat](obj, filename)


def get_files(directory='.', recursive=False):
    '''Detect metadata files in given directory'''
    if recursive:
        traverse = os.walk(directory)
    else:
        traverse = (next(os.walk(directory)),)
    for parent, dirs, files in traverse:
        for filename in files:
            full_path = os.path.join(parent, filename)
            if is_metadata(full_path):
                yield full_path


def detect_format(filename):
    _, extension = os.path.splitext(filename)
    if extension == '.syml':
        return 'StrictYAML'
    elif extension == '.json':
        return 'JSON'
    else:
        raise ValueError('can not detect file format for {}'.format(filename))


def is_metadata(filename):
    try:
        detect_format(filename)
        return True
    except ValueError:
        return False


def load_strict_yaml(filename):
    with open(filename) as f:
        serialized = f.read()
        strictyaml.load(serialized).data


def load_json(filename):
    with open(filename) as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def write_strict_yaml(data, filename):
    # TODO: https://github.com/crdoconnor/strictyaml/issues/43
    with open(filename, 'w') as f:
        f.write(strictyaml.as_document(data).as_yaml())


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
