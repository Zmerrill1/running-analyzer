from decouple import config
from sqlmodel import SQLModel, create_engine

DATABASE_URL = config("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_engine():
    return engine
