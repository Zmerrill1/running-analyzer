from decouple import config
from sqlmodel import SQLModel, create_engine

DATABASE_URL = config("DATABASE_URL")


def get_engine():
    return create_engine(DATABASE_URL, echo=True)


def init_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
