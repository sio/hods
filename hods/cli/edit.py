'''
{hods} {subcommand} [FILENAME1] [FILENAME2] ...

    Edit metadata file(s) in default $EDITOR

    Data hashes are updated automatically after editing
'''


import os
import subprocess
import sys
from shutil import which

from hods._lib.files import get_files, backup
from hods.cli import check, rehash


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']

    files = set(a for a in args[2:] if (a and not a.startswith('--')))
    if not files: files = list(get_files())

    editor = detect_editor()

    check.main(*files)
    for filename in files:
        print('Editing {filename} with {editor}'.format(**locals()))
        with backup(filename):
            retcode = subprocess.call([editor, filename])
            if retcode:
                sys.exit(retcode)
            rehash.main(filename)


def detect_editor():
    '''Detect the command to launch default text editor'''
    variables = [
        'EDITOR',
        'VISUAL',
    ]
    fallback = [
        'vim',
        'vi',
        'nano',
        'notepad.exe',
    ]
    editor = None

    # Try environment variables first
    for var in variables:
        editor = os.environ.get(var)
        if editor:
            return editor

    # Fall back to hardcoded values
    for command in fallback:
        if which(command):
            return command

    raise ValueError(
        'Can not detect default text editor. '
        'Try setting $EDITOR environment variable'
    )
