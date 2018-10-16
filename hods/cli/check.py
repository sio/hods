'''
{hods} {subcommand} --recursive [FILENAME1] [FILENAME2] ...

    Check hash values and validate schemas for metadata file(s).
'''


import sys
from urllib.error import HTTPError

from hods import (
    Metadata,
    ValidationErrors,
    HashMismatchError,
)
from hods._lib.files import get_files


RECURSIVE_FLAG = '--recursive'


def main():
    args = sys.argv + ['', '']

    if RECURSIVE_FLAG in args:
        recursive = True
        args.pop(args.index(RECURSIVE_FLAG))
    else:
        recursive = False

    files = set(a for a in args[2:] if a)
    if not files: files = get_files(recursive=recursive)

    exit_code = 0
    for filename in files:
        print('Checking {}: '.format(filename), end='')
        meta = None
        try:
            meta = Metadata(filename=filename)
        except ValidationErrors:
            print('SCHEMA ERROR')
            exit_code = 1
        except FileNotFoundError:
            print('FILE NOT FOUND')
            exit_code = 1
        except HTTPError:
            print('HTTP ERROR')
            exit_code = 1
        except Exception:
            print('PARSE ERROR')
            exit_code = 1

        if not meta: continue

        try:
            meta.validate_hashes()
            print('OK')
        except HashMismatchError:
            print('HASH ERROR')
            exit_code = 1
    sys.exit(exit_code)
