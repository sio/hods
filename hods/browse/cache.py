'''
Sqlite-backed cache for multiple HODS documents
'''


import os.path
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
)



class DocumentsReadOnlyCache:
    '''
    Caching and searching interface to a collection of HODS documents
    '''


    def __init__(self, cache_db):
        '''Initialize cache database in file provided by path'''
        self.db = create_engine(
            'sqlite:///{}'.format(os.path.abspath(cache_db))
        )
        Base.metadata.create_all(self.db)  # no-op if database is not new
        self.sessionmaker = sessionmaker(bind=self.db)


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

    id         = Column(Integer, primary_key=True, autoincrement=True)
    path       = Column(
                    String,
                    ForeignKey('files.path', ondelete='CASCADE', onupdate='CASCADE')
                 )  # TODO: foreign_keys enforcement is disabled by default in sqlite
    key        = Column(String)
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
