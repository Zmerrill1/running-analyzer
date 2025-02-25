from decouple import config
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = config("DATABASE_URL")
ECHO = config("ECHO", default=False, cast=bool)
engine = create_engine(DATABASE_URL, echo=ECHO)


def get_engine():
    return engine


def get_session():
    return Session(engine)


def init_db():
    SQLModel.metadata.create_all(engine)
