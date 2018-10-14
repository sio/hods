'''
Custom exceptions used in HODS package
'''


from abc import ABCMeta
import jsonschema.exceptions


class ValidationError(Exception, metaclass=ABCMeta):
    '''
    This error must be raised when a data structure does not match the
    corresponding schema.

    Exceptions provided by third party modules are wrapped using the abstract
    base class functionality.
    '''
    pass


# Support for exceptions provided by third party modules
ThirdPartyValidationErrors = (
    jsonschema.exceptions.ValidationError,
)
for cls in ThirdPartyValidationErrors:
    ValidationError.register(cls)
