'''
Usage:
    {hods} {subcommand} [--type=ClassName] [FILENAME1] [FILENAME2] ...

Create metadata file(s) and open them for editing.

Supports specifying HODS metadata class names like `--type=Metadata` (default)
or arbitrary Python classes with full import path, e.g:
`--type=package.module.CustomMetadata`
'''


import sys
from importlib import import_module

from hods.cli import edit


TYPE_FLAG = '--type='
DEFAULT_TYPE = 'Metadata'
DEFAULT_FILENAME = 'data.hods.yml'


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']

    if args[2].startswith(TYPE_FLAG):
        class_name = args.pop(2).replace(TYPE_FLAG, '', 1)
    else:
        class_name = DEFAULT_TYPE

    if '.' not in class_name:
        class_name = 'hods.' + class_name

    module, member = class_name.rsplit('.', 1)

    try:
        class_meta = getattr(import_module(module), member)
    except ImportError:  # avoid confusing the hods.cli._main error handler
        raise ValueError('invalid metadata type: {}'.format(class_name))

    files = set(a for a in args[2:] if (a and not a.startswith('--')))
    if not files:
        files = (DEFAULT_FILENAME,)

    for filename in files:
        meta = class_meta()
        meta.validate_hashes(write_updates=True)
        meta.write(filename)
        edit.main(filename)
