'''
Usage:
    {hods} {subcommand} [--sections=SECTION1,SECTION2|--sections-all]
            [FILENAME1] [FILENAME2] ...

Update hash values for metadata file(s).

If the names of sections are provided, hashes will be calculated only for those
sections.

If no section names are provided, hashes will be calculated only for sections
that already have some previous hash value.
'''


import sys

from hods import Metadata, HashMismatchError
from hods._lib.files import get_files


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']

    sections = []
    all_sections = False

    if args[2] == '--sections-all':
        args.pop(2)
        all_sections = True
    elif args[2].startswith('--sections'):
        sections = args[2].split('=')[1].split(',')
        args.pop(2)

    files = set(a for a in args[2:] if a)
    if not files: files = get_files()

    for filename in files:
        meta = Metadata(filename=filename)
        if all_sections:
            sections = [x for x in meta if x != 'info']
        try:
            meta.validate_hashes(sections=sections)
            print('No changes required for: {}'.format(filename))
        except HashMismatchError:
            meta.validate_hashes(sections=sections, write_updates=True)
            meta.write()
            print('Data hashes updated for: {}'.format(filename))
