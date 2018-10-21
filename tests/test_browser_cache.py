'''
Tests for SQLite-backed cache engine
'''


from unittest import TestCase

from hods.browse.cache import DocumentsReadOnlyCache, File


class testCacheORM(TestCase):

    def test_creating_database(self):
        cache = DocumentsReadOnlyCache('/tmp/cache_file.db')
        with cache.session() as session:
            f = File(path='hello')
            session.add(f)
        import pdb; pdb.set_trace()

