'''
Logger setup
'''


import logging
import os


_package = __name__.split('.')[0]  # top-level package
log = logging.getLogger(_package)

if not log.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

if os.environ.get('HODS_DEBUG'):
    log.setLevel(logging.DEBUG)
else:
    log.setLevel(logging.INFO)
