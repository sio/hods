'''
Unit tests for custom exceptions
'''

from unittest import TestCase

import jsonschema.exceptions

from hods import ValidationError


class testValidationError(TestCase):

    def test_initialization(self):
        err = ValidationError()

    def test_jsonschema_error(self):
        self.assertTrue(isinstance(
            jsonschema.exceptions.ValidationError(''),
            ValidationError
        ))

    def test_raising_child_catching_parent(self):
        with self.assertRaises(ValidationError):
            raise jsonschema.exceptions.ValidationError('')

    def test_catching_parent_exception(self):
        try:
            raise jsonschema.exceptions.ValidationError('')
        except ValidationError:
            pass
