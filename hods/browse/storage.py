'''
Tools used to store cache files between browser runs
'''


import os.path
from hashlib import md5
from base64 import b32encode

from appdirs import AppDirs


def get_cachefile(target):
    '''
    Calculate full path to cache file for any given target directory
    '''
    dirname = get_cachedir()
    filename = make_cachename(target)
    return os.path.join(dirname, filename)


def get_cachedir():
    '''
    Detect the directory used to store HODS browser cache
    '''
    dirs = AppDirs('hods')
    return dirs.user_cache_dir


def make_cachename(target):
    '''
    Generate cache file name for each target directory. It has to be unique
    (almost) and short.
    '''
    template = 'browse-{id}'
    hashed = md5(target.encode()).digest()
    shortened = b32encode(hashed).decode().rstrip('=')
    return template.format(id=shortened)
