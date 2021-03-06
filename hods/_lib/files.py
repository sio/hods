'''
File operations for HODS

Supported file formats:
    - JSON - .json extension
    - StrictYAML - YAML files with .syml extension
    - YAML - vanilla YAML files with .yml or .yaml extension
'''
# Checklist for adding support of new formats:
#   - get_object
#   - write_object
#   - detect_format
#   - module docsctring


import os
import json
import shutil
from collections import OrderedDict
from contextlib import contextmanager
import strictyaml
from ruamel import yaml


def get_object(filename, fileformat=None):
    '''Read serialized object from file. Detect file format if not specified'''
    if not fileformat:
        fileformat = detect_format(filename)
    loaders = {
        'JSON':       load_json,
        'StrictYAML': load_strict_yaml,
        'YAML':       load_yaml,
    }
    return loaders[fileformat](filename)


def write_object(obj, filename, fileformat=None, suffix='.hods~'):
    '''Write serialized object to file. Detect file format if not specified'''
    if not filename:
        raise ValueError('can not write data without filename')
    if not fileformat:
        fileformat = detect_format(filename)

    writers = {
        'JSON':       write_json,
        'StrictYAML': write_strict_yaml,
        'YAML':       write_yaml,
    }

    with backup(filename, suffix):
        writers[fileformat](obj, filename)


@contextmanager
def backup(filename, suffix='.hods~'):
    '''Context manager to execute dangerous file operations with backup'''
    suffix_for_duplicates = '{num}~'
    backup_created = False

    # Create backup file with given suffix
    if suffix:
        backup_name = filename + suffix
        backup_number = 0
        while os.path.exists(backup_name):  # never overwrite previous backups
            backup_number += 1
            backup_name = \
                filename  \
                + suffix  \
                + suffix_for_duplicates.format(num=backup_number)
        try:
            shutil.copyfile(filename, backup_name)
            backup_created = True
        except FileNotFoundError:  # no need to backup non-existent files
            pass

    # Do dangerous stuff that may raise exceptions
    yield

    # If no exceptions were raised, remove backup file
    if backup_created:
        os.remove(backup_name)


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
    _, extension = os.path.splitext(filename.lower())
    if extension == '.syml':
        return 'StrictYAML'
    elif extension == '.json':
        return 'JSON'
    elif extension in {'.yml', '.yaml'}:
        return 'YAML'
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
        return strictyaml.load(serialized).data


def load_yaml(filename):
    with open(filename) as f:
        return yaml.load(f, Loader=yaml.RoundTripLoader)


def load_json(filename):
    with open(filename) as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def write_strict_yaml(data, filename):
    # TODO: https://github.com/crdoconnor/strictyaml/issues/43
    with open(filename, 'w') as f:
        f.write(strictyaml.as_document(data).as_yaml())


# Dump OrderedDicts as simple dictionaries
yaml.add_representer(OrderedDict, yaml.RoundTripDumper.represent_dict, Dumper=yaml.RoundTripDumper)

def write_yaml(data, filename):
    with open(filename, 'w') as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            Dumper=yaml.RoundTripDumper,
        )


def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
