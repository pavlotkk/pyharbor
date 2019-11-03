from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import TYPE_CHECKING

from harbor import conf

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as SqlSession

engine = create_engine(conf.DB_CONNECTION_STRING)

Base = declarative_base()


def drop_all():
    Base.metadata.drop_all(engine)


def create_all():
    Base.metadata.create_all(engine)


def create_session() -> 'SqlSession':
    session_factory = sessionmaker(bind=engine)
    return session_factory()
