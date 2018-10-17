'''
Usage: {hods} SUBCOMMAND [ARGUMENTS]
       {hods} help SUBCOMMAND

Manage structured data stored in plain text files with YAML or JSON formatting.

Available subcommands:
{subcommands}

To view help message for a specific subcommand use:
    {hods} help SUBCOMMAND

Copyright 2018 Vitaly Potyarkin
    https://github.com/sio/hods

This program is Free Software and comes with ABSOLUTELY NO WARRANTY,
to the extent permitted by applicable law. For more information see:
    http://www.apache.org/licenses/LICENSE-2.0
'''

import os.path
import pkgutil
import sys
import textwrap
from importlib import import_module


EXECUTABLE = os.path.basename(sys.argv[0])


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
    show_help = arguments[1] in {'help', '--help', '--usage', '-h'}

    if show_help:
        subcommand = arguments[2]
    else:
        subcommand = arguments[1]
    if not subcommand:
        return usage()

    try:
        submodule = import_module('.' + subcommand, __package__)
        if show_help or arguments[2] == '--help':
            try:
                submodule.help()
            except AttributeError:
                message = submodule.main.__doc__
                if not message or not message.strip():
                    message = submodule.__doc__
                show_help_message(message.format(
                    hods=EXECUTABLE,
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
    path = os.path.dirname(__file__)
    subcommands = []
    for _, name, is_package in pkgutil.iter_modules([path,]):
        if not is_package and not name.startswith('_'):
            subcommands.append(name)

    show_help_message(__doc__.format(
        hods=EXECUTABLE,
        subcommands='\n'.join('    %s' % sub for sub in sorted(subcommands))
    ))


def show_help_message(message):
    '''
    Fix indentation and trailing whitespace in the message before printing
    it to stdout
    '''
    print(textwrap.dedent(message).strip())
