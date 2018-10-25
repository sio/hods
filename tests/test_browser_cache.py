'''
Tests for SQLite-backed cache engine
'''


import os.path
from tempfile import TemporaryDirectory
from unittest import TestCase, skip

from hods.browse.cache import DocumentsReadOnlyCache, File, Content, Info



class testCacheORM(TestCase):

    @skip('Does not work. SQLite file is not freed and can not be deleted')
    def test_creating_database(self):
        with TemporaryDirectory(prefix='hods_tests_') as tempdir:
            cache = DocumentsReadOnlyCache(os.path.join(tempdir, 'cache.db'))
            cache._reinit_db()
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
            #del(cache)
