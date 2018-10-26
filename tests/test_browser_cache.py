'''
Tests for SQLite-backed cache engine
'''


from unittest import TestCase, skip

from hods.browse.cache import DocumentsReadOnlyCache, File, Content, Info



class testCacheORM(TestCase):

    def test_creating_database(self):
        cache = DocumentsReadOnlyCache(':memory:')
        with cache.session() as session:
            f = File(path='hello')
            c = Content(path='hello', key='1')
            c1 = Content(path='hello world', key='2')
            session.add(f)
            session.add(c)
            session.add(c1)
        with cache.session() as s:
            f = s.query(File).first()
            s.delete(f)
        with cache.session() as s:
            self.assertEqual(len(session.query(Content).all()), 1)

    def test_adding_to_cache(self):
        cache = DocumentsReadOnlyCache(':memory:')

        cache.add('tests/data/samples/sample-v1-02.json')
        with cache.session() as session:
            session.add(File(path='hello'))             # must be cleaned up, because seen == None
            session.add(File(path='world', seen=123))   # seen != cache.timestamp

        cache.drop_outdated()
        with cache.session() as session:
            files = [f.path for f in session.query(File)]
        self.assertEqual(len(files), 1)
