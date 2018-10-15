'''
Command line interface for HODS
'''

import sys
import textwrap
from importlib import import_module


def main():
    '''
    Main entry point for CLI commands

    Subcommands are defined in other modules of this package. Each module has
    to provide the main() function.

    If help() function is provided, it will be used to display usage message
    for that subcommand, otherwise the usage message will be generated from the
    `main()` docstring or the module docstring.
    '''
    arguments = sys.argv + [None, None]
    show_help = arguments[1] == 'help'

    if show_help:
        subcommand = arguments[2]
    else:
        subcommand = arguments[1]
    if not subcommand:
        return usage()

    try:
        submodule = import_module('.' + subcommand, __package__)
        if show_help or arguments[2] == 'help':
            try:
                submodule.help()
            except AttributeError:
                message = submodule.main.__doc__
                if not message or not message.strip():
                    message = submodule.__doc__
                show_help_message(message.format(
                    hods=arguments[0],
                    subcommand=subcommand,
                ))
        else:
            submodule.main()
    except ImportError:
        # TODO: add handler for third-party subcommands, like `hods-subcommand`
        print(
            'Unsupported subcommand: {}\n'.format(subcommand),
            file=sys.stderr,
            flush=True
        )
        usage()
        sys.exit(1)


def usage():
    '''Show usage message'''
    show_help_message(__doc__)  # TODO: replace this stub


def show_help_message(message):
    '''
    Fix indentation and trailing whitespace in the message before printing
    it to stdout
    '''
    print(textwrap.dedent(message).strip())
