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
ThirdPartyValidationErrors = (
    jsonschema.exceptions.ValidationError,
)
for cls in ThirdPartyValidationErrors:
    ValidationError.register(cls)
