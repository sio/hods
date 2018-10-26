'''
Sqlite-backed cache for multiple HODS documents
'''


import os
import time
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    Query,
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import NullPool

from hods import Metadata
from hods._lib.core import is_mapping
from hods._lib.files import get_files


SEPARATOR = '.'  # separates nested keys when flattening tree data


class DocumentsReadOnlyCache:
    '''
    Caching and searching interface to a collection of HODS documents
    '''
    SCHEMA_VERSION = ('version', '1')  # used to drop outdated cache files


    def __init__(self, cache_db):
        '''Initialize cache database in file provided by path'''
        self.filename = cache_db if cache_db==':memory:' else os.path.abspath(cache_db)
        self.timestamp = int(time.time())
        self._init_db()
        if not self._check_version():
            self._init_db(reinit=True)


    @contextmanager
    def session(self):
        '''Context manager for database sessions'''
        short_session = self.sessionmaker()
        try:
            yield short_session
            short_session.commit()
        except:
            short_session.rollback()
            raise
        finally:
            short_session.close()


    def _check_version(self):
        '''Check that cache file uses current database schema'''
        version_key, version_valid = self.SCHEMA_VERSION

        with self.session() as session:
            try:
                version = session.query(Info).filter(Info.option == version_key).first()
                return bool(version and version.value == version_valid)
            except OperationalError:
                return False


    def _init_db(self, reinit=False):
        '''(Re)initialize empty cache database'''
        in_memory = self.filename == ':memory:'

        if reinit and not in_memory and os.path.exists(self.filename):
            os.remove(self.filename)

        if in_memory:
            connection_url = 'sqlite://'
        else:
            connection_url = 'sqlite:///{}'.format(self.filename)

        self.db = create_engine(connection_url)
        Base.metadata.create_all(self.db)
        self.sessionmaker = sessionmaker(bind=self.db)

        if reinit:
            version_key, version_valid = self.SCHEMA_VERSION
            version = Info(option=version_key, value=version_valid)
            with self.session() as session:
                session.add(version)


    def add(self, filename=None, directory=None):
        '''Add HODS data files to cache'''
        if filename is not None and directory is not None:
            raise ValueError('only one argument is allowed: either filename or directory')
        elif filename is not None:
            files = [filename,]
        elif directory is not None:
            files = get_files(directory, recursive=True)
        else:
            files = []

        for datafile in files:
            with self.session() as session:
                datafile = os.path.abspath(datafile)

                # Check if file is already in cache and that cache is valid
                current = os.stat(datafile)
                size, ctime, mtime = map(int, (current.st_size, current.st_ctime, current.st_mtime))
                cached = session.query(File).filter(File.path == datafile).first()
                cache_is_valid = \
                    cached is not None and \
                    (size, ctime, mtime) == (cached.size, cached.ctime, cached.mtime)
                if cache_is_valid:
                    cached.seen = self.timestamp
                    continue

                # Drop outdated caches, skip invalid documents
                if cached is not None:
                    session.delete(cached)
                try:
                    content = Metadata(filename=datafile)
                except Exception:
                    continue

                # Add file description to cache
                file_ = File()
                file_.path  = datafile
                file_.size, file_.ctime, file_.mtime = size, ctime, mtime
                file_.seen  = self.timestamp
                session.add(file_)

                # Add file contents to cache
                for row in walk_tree(content):
                    record = Content(
                        path    = datafile,
                        fullkey = row.fullkey,
                        prefix  = row.prefix,
                        key     = row.key,
                        value   = row.value,
                        is_leaf = row.leafnode,
                    )
                    session.add(record)


    def drop(self, filename):
        '''Remove file decription and its contents from cache'''
        filename = os.path.abspath(filename)
        with self.session() as session:
            session.query(File).filter(File.path == filename).delete()


    def drop_outdated(self):
        '''Clear all outdated cache entries'''
        # Content entries are removed automatically thanks to SQLAlchemy
        # relationship(cascade=...) feature
        with self.session() as session:
            session.query(File).filter( \
                (File.seen != self.timestamp) | (File.seen == None) \
            ).delete()


    def get(self, attrs, steps=(), by_value=False):
        '''
        Iterate over the content filtered with simplified query steps.
        Duplicate entries are not repeated.

        Return values of specified fields (attrs).
        '''
        if isinstance(attrs, str):
            attrs = (attrs,)
        query = self._make_query(tuple(attrs), tuple(steps), by_value)
        with self.session() as session:
            yield from query.with_session(session)


    @lru_cache(maxsize=64)
    def _make_query(self, attrs=None, steps=None, by_value=False):
        '''
        Build a database query to retrieve unique values corresponding to the
        sequence of hierarchy steps in the tree data structure
        '''
        if not steps:
            prefix = None
        else:
            prefix = SEPARATOR.join(steps)
        if not attrs:
            target = Content
        else:
            target = [getattr(Content, a) for a in attrs]
        if not by_value:
            condition = (Content.prefix == prefix)
        else:
            condition = (Content.fullkey == prefix)
        return Query(target).filter(condition).distinct()


TreeRow = namedtuple('TreeRow', 'fullkey,prefix,key,value,leafnode')
def walk_tree(tree, prefix=None):
    '''
    Flatten tree data into a sequence of rows
    (keys and values are coerced into strings)
    '''
    for key in tree:  # Metadata objects have no .items() method
        value = tree[key]
        key = str(key)
        if prefix:
            full = SEPARATOR.join((prefix, key))
        else:
            full = key
        if is_mapping(value):
            yield TreeRow(full, prefix, key, None, False)
            yield from walk_tree(value, full)
        else:
            yield TreeRow(full, prefix, key, str(value), True)


#
# SQLAlchemy configuration
#


Base = declarative_base()


class File(Base):
    '''List of files added to cache'''
    __tablename__ = 'files'

    path  = Column(String, primary_key=True)
    size  = Column(Integer)
    mtime = Column(Integer)
    ctime = Column(Integer)
    seen  = Column(Integer)

    content = relationship(
                    'Content',
                    back_populates='file',
                    cascade='delete, delete-orphan',
                )




class Content(Base):
    '''Full contents for all files added to cache'''
    __tablename__ = 'content'

    path    = Column(
                 String,
                 ForeignKey('files.path', ondelete='CASCADE', onupdate='CASCADE'),
                 primary_key=True
              )
    fullkey = Column(String, primary_key=True)
    prefix  = Column(String)
    key     = Column(String)
    value   = Column(String)
    is_leaf = Column(Boolean)
    seen    = Column(Integer)

    file    = relationship('File', back_populates='content')



class Info(Base):
    '''Some metadata about the cache file itself (key-value pairs)'''
    __tablename__ = 'info'

    option = Column(String, primary_key=True)
    value  = Column(String)
