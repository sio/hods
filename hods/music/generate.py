'''
Usage:
    {hods} {subcommand} [--target=album_hods.yml] [--recursive]
        DIRECTORY1 [DIRECTORY2] ...

Read music metadata from album directories. Each directory is assumed to
contain a single album. Nested subdirectories are not evaluated.

By default parsed metadata is saved into a `album_hods.yml` file in each
album directory. If --target argument is provided, its value is used as the
filename instead.
'''


import os
import sys

from hods.music.objects import MusicAlbumInfo
from hods.cli import _flags as flags


TARGET_FLAG = '--target='
TARGET_DEFAULT = 'album_hods.yml'


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']

    if flags.RECURSIVE in args:
        recursive = True
        args.pop(args.index(flags.RECURSIVE))
    else:
        recursive = False

    target = TARGET_DEFAULT
    for a in args:
        if a.startswith(TARGET_FLAG):
            target = a.replace(TARGET_FLAG, '', 1)
            args.pop(args.index(a))

    directories = set(a for a in args[2:] if a)

    for dirname in directories:
        filename = os.path.join(dirname, target)
        if os.path.exists(filename):
            print('Metadata file already exists: {}'.format(filename))
            continue
        meta = MusicAlbumInfo()
        meta.parse(dirname)
        if len(meta.data.tracks):
            meta.write(filename)
            print('Metadata written: {}'.format(filename))

        if recursive:
            parent, subdirs, files = next(os.walk(dirname))
            main(
                flags.RECURSIVE,
                *(os.path.join(parent, subdir) for subdir in subdirs)
            )
