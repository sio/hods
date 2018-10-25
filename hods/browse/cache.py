'''
Sqlite-backed cache for multiple HODS documents
'''


import os
from contextlib import contextmanager

from sqlalchemy import (
    BigInteger,
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
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import NullPool



class DocumentsReadOnlyCache:
    '''
    Caching and searching interface to a collection of HODS documents
    '''
    SCHEMA_VERSION = ('version', '1')  # used to drop outdated cache files


    def __init__(self, cache_db):
        '''Initialize cache database in file provided by path'''
        self.filename = os.path.abspath(cache_db)
        self.db = create_engine('sqlite:///{}'.format(self.filename))
        self.sessionmaker = sessionmaker(bind=self.db)
        if not self._check_version():
            self._reinit_db()


    def __del__(self):
        '''Clean up'''
        self.db.dispose()  # clear the connections pool


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


    def _reinit_db(self):
        '''(Re)initialize empty cache database'''
        if os.path.exists(self.filename):
            os.remove(self.filename)

        self.db = create_engine('sqlite:///{}'.format(self.filename))
        Base.metadata.create_all(self.db)
        self.sessionmaker = sessionmaker(bind=self.db)

        version_key, version_valid = self.SCHEMA_VERSION
        version = Info(option=version_key, value=version_valid)
        with self.session() as session:
            session.add(version)


    def add(self, filename=None, directory=None):
        pass


    def drop(self, filename):
        pass



Base = declarative_base()


class File(Base):
    '''List of files added to cache'''
    __tablename__ = 'files'

    path  = Column(String, primary_key=True)
    size  = Column(BigInteger)
    mtime = Column(DateTime)
    ctime = Column(DateTime)
    seen  = Column(String)

    content = relationship(
                    'Content',
                    back_populates='file',
                    cascade='delete, delete-orphan',
                )




class Content(Base):
    '''Full contents for all files added to cache'''
    __tablename__ = 'content'

    path       = Column(
                    String,
                    ForeignKey('files.path', ondelete='CASCADE', onupdate='CASCADE')
                 )  # TODO: foreign_keys enforcement is disabled by default in sqlite
    key        = Column(String, primary_key=True)
    key_prefix = Column(String)
    key_suffix = Column(String)
    value      = Column(String)
    is_leaf    = Column(Boolean)

    file       = relationship('File', back_populates='content')



class Info(Base):
    '''Some metadata about the cache file itself (key-value pairs)'''
    __tablename__ = 'info'

    option = Column(String, primary_key=True)
    value  = Column(String)
