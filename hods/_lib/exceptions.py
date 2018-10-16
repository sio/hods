'''
Custom exceptions used in HODS package
'''


from abc import ABCMeta
import jsonschema.exceptions
from hods import __name__ as _top_level_module


class ValidationError(Exception, metaclass=ABCMeta):
    '''
    This error must be raised when a data structure does not match the
    corresponding schema.

    Exceptions provided by third party modules are wrapped using the abstract
    base class functionality.
    '''
    __module__ = _top_level_module


# Support for exceptions provided by third party modules
ThirdPartyValidationErrors = [
    jsonschema.exceptions.ValidationError,
]
for cls in ThirdPartyValidationErrors:
    ValidationError.register(cls)


# Unfortunately, abstract base classes do not work in `except` clause in Python 3:
# - https://bugs.python.org/issue12029
# - https://stackoverflow.com/questions/23890645
ValidationErrors = tuple(ThirdPartyValidationErrors + [ValidationError])


class HashMismatchError(Exception):
    '''Raised when data hash does not match the stored value'''
    __module__ = _top_level_module
