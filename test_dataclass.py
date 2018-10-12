'''
Unit tests for data classes
'''

from unittest import TestCase

from dataclass import TreeStructuredData as TSD


class testTreeWrapper(TestCase):
    sample = {
        'hello': 'world',
        'tree': {
            'inner': 'value',
            'second': {
                'level': 'of nesting',
            },
            'list': [1,2,3,4],
            'tuple': (5,6,7),
        },
    }

    def test_nesting(self):
        data = TSD(self.sample)
        self.assertEqual(data.hello, 'world')
        self.assertEqual(data.tree.inner, 'value')
        self.assertEqual(data.tree.second.level, 'of nesting')
