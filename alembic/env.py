from logging.config import fileConfig
from sqlmodel import SQLModel
from alembic import context
from decouple import config
from running_analyzer.db import Database


# Alembic Config
config_obj = context.config

# Load environment variables
DATABASE_URL = config("DATABASE_URL")
config_obj.set_main_option("sqlalchemy.url", DATABASE_URL)

# Setup logging
if config_obj.config_file_name is not None:
    fileConfig(config_obj.config_file_name)

# Target metadata for migrations
target_metadata = SQLModel.metadata


def run_migrations_online():
    db = Database(DATABASE_URL)
    connectable = db.get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    context.configure(
        url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
