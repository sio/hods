'''
Classes for the structured data
'''


from collections.abc import Mapping


class TreeStructuredData:
    '''
    Generic metadata class.

    Handles reading, modification and validation of data structure. Checks
    hashes all the time.
    '''
    def __init__(self, data, parent=None):
        if not _ismapping(data):
            raise ValueError(
                "{cls}() expected a mapping object but received '{data}'".format(
                    cls = type(self).__name__,
                    data = type(data).__name__,
                )
            )
        self._data = data
        self._parent = parent
        self._children = dict()

    def validate(self):
        if self._parent is None:
            print('Validating %s' % self)
        else:
            self._parent.validate()

    def __getattr__(self, attr):
        if attr in self._children:
            response = self._children[attr]
        elif attr in self._data:
            if _ismapping(self._data[attr]):
                response = self._children[attr] = \
                    type(self)(data=self._data[attr], parent=self)
            else:
                response = self._data[attr]
        else:
            raise AttributeError(
                "'{cls}' object has no attribute '{attr}'".format(
                    cls=self.__class__.__name__,
                    attr=attr
                )
            )
        return response

    def __repr__(self):
        return '<{cls}({data}{parent})>'.format(
            cls = self.__class__.__name__,
            data = self._data,
            parent = ', <child of #%s>' % id(self._parent) if self._parent else ''
        )



class TranslatorWrapper:
    '''
    Helper class to simplify class composition and wrapping properties

    THIS IS NOT NECESSARY. SIMPLY DEFINE REQUIRED METHODS AND PROPERTIES IN
    AlbumMetadata
    '''
    pass


class AlbumMetadata:
    '''
    Stable API for music album metadata
    '''
    pass


def _ismapping(value):
    '''Check if argument value is mapping'''
    return isinstance(value, Mapping)
