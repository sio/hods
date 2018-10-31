'''
Usage:
    {hods} {subcommand} DIRECTORY

Launch interactive shell to browse all documents in specified directory
'''


import os
import sys

from hods.browse.shell import DocumentBrowser
from hods.browse.storage import get_cachefile


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']
    target = args[2] or '.'

    cache_file = get_cachefile(target)
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    shell = DocumentBrowser(cache_file, target)
    shell.cmdloop()
