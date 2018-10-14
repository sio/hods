'''
Calculate hashes of structured data regardless of its format
'''


import json
from hashlib import (
    md5,
    sha256,
)


def struct_hash(data, algorithm='sha256'):
    '''
    Calculate hash of structured data that can be serialized into JSON
    '''
    hashes = {
        'md5':    lambda byte: md5(byte).hexdigest(),
        'sha256': lambda byte: sha256(byte).hexdigest(),
    }
    datastring = json.dumps(
        data,
        indent=None,
        separators=',:',
        sort_keys=True,  # TODO: does this sorting depend on locale?
    )
    databytes = datastring.encode()
    return hashes[algorithm](databytes)


def datahash(container, algorithm='sha256'):
    '''
    Calculate data hash for HODS container object
    '''
    return struct_hash(container._data, algorithm)
