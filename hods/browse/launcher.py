'''
Usage:
    {hods} {subcommand} DIRECTORY

Launch interactive shell to browse all documents in specified directory
'''


import sys

from hods.browse.shell import DocumentBrowser


def main(*args):
    if args:
        args = ['', ''] + list(args) + ['', '']
    else:
        args = sys.argv + ['', '']
    target = args[2] or '.'

    cache_file = ':memory:'  # TODO: use persistent cache
    shell = DocumentBrowser(cache_file, target)
    shell.cmdloop()
