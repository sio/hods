'''
Tests for SQLite-backed cache engine
'''


from unittest import TestCase, skip

from hods.browse.cache import DocumentsReadOnlyCache, File, Content, Info



class testCacheORM(TestCase):

    def setUp(self):
        self.cache = DocumentsReadOnlyCache(':memory:')

    def test_creating_database(self):
        cache = self.cache
        with cache.session() as session:
            f = File(path='hello')
            c = Content(path='hello', fullkey='1')
            c1 = Content(path='hello world', fullkey='2')
            session.add(f)
            session.add(c)
            session.add(c1)
        with cache.session() as s:
            f = s.query(File).first()
            s.delete(f)
        with cache.session() as s:
            self.assertEqual(len(session.query(Content).all()), 1)

    def test_adding_to_cache(self):
        cache = self.cache
        cache.add('tests/data/samples/sample-v1-02.json')
        with cache.session() as session:
            session.add(File(path='hello'))             # must be cleaned up, because seen == None
            session.add(File(path='world', seen=123))   # seen != cache.timestamp

        cache.drop_outdated()
        with cache.session() as session:
            files = [f.path for f in session.query(File)]
        self.assertEqual(len(files), 1)

    def test_reading_cache(self):
        cache = self.cache
        cache.add('tests/data/samples/sample-v1-02.json')
        cache.add('tests/data/samples/sample-v1-03-remote_schema.json')
        top = list(cache.get('key'))
        tuples = list(cache.get('key,is_leaf'.split(',')))
        files = list(cache.get('path'))
        self.assertEqual(len(files), 2)
        self.assertEqual(len(top), 3) # info, data, extra
