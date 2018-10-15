'''
Launcher script for HODS command line application
'''


# Thanks to the authors of `unittest` module from standard library:
import sys
if sys.argv[0].endswith('__main__.py'):
    import os.path
    # We change sys.argv[0] to make help message more useful
    # use executable without path, unquoted
    # (it's just a hint anyway)
    # (if you have spaces in your executable you get what you deserve!)
    executable = os.path.basename(sys.executable)
    sys.argv[0] = executable + ' -m ' + __package__
    del os


from hods.cli import main


if __name__ == '__main__':
    main()
