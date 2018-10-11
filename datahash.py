'''
Calculate hashes of structured data regardless of its format
'''


import json
from hashlib import sha256


def datahash(data):
    '''
    Calculate hash of structured data that can be serialized into JSON
    '''
    hashfunc = lambda byte: sha256(byte).hexdigest()
    datastring = json.dumps(
        data,
        indent=None,
        separators=',:',
        sort_keys=True,  # TODO: does this sorting depend on locale?
    )
    databytes = datastring.encode()
    return hashfunc(databytes)

