'''
Calculate hashes of structured data regardless of its format
'''


import json
import hashlib


def struct_hash(data, algorithm='sha256'):
    '''
    Calculate hash of structured data that can be serialized into JSON
    '''
    datastring = json.dumps(
        data,
        indent=None,
        separators=',:',
        sort_keys=True,  # TODO: does this sorting depend on locale?
    )
    databytes = datastring.encode()

    if algorithm in hashlib.algorithms_guaranteed:
        hasher = getattr(hashlib, algorithm)
        return hasher(databytes).hexdigest()
    else:
        raise ValueError('unsupported hashing algorithm: {}'.format(algorithm))


def datahash(container, algorithm='sha256'):
    '''
    Calculate data hash for HODS container object
    '''
    return struct_hash(container._data, algorithm)
