from decouple import config
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional
from running_analyzer.models import Run
from datetime import datetime


class Database:
    def __init__(self, database_url: str | None = None, debug: bool | None = None):
        self.database_url = database_url or config("DATABASE_URL")
        self.debug = (
            debug if debug is not None else config("ECHO", default=False, cast=bool)
        )
        self.engine = create_engine(self.database_url, echo=self.debug)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return Session(self.engine)

    def init_db(self):
        SQLModel.metadata.create_all(self.engine)


class RunRepository:
    def __init__(self, Database):
        self.db = Database()
        self.session = self.db.get_session()

    def get_run_by_id(self, run_id: int) -> Optional[Run]:
        with self.session() as session:
            return session.get(Run, run_id)

    def list_runs(self) -> list[Run]:
        with self.session() as session:
            statement = select(Run)
            return session.exec(statement).all()

    def add_run(self, run: Run) -> Run:
        with self.session() as session:
            session.add(Run)
            session.commit()
            session.refresh(run)
            return run

    def delete_run(self, run_id: int) -> bool:
        with self.session() as session:
            run = session.get_run_by_id(run_id)
            if run:
                session.delete(run)
                session.commit()
                return True
            return False

    def update_run(self, run: Run, **kwargs) -> None:
        with self.session() as session:
            for key, value in kwargs.items():
                setattr(run, key, value)
            session.add(run)
            session.commit()

    def list_runs_by_type(self, run_type: str) -> list[Run]:
        with self.session() as session:
            statement = select(Run).where(Run.run_type == run_type)
            return session.exec(statement).all()

    def list_runs_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Run]:
        with self.session() as session:
            statement = select(Run).where(Run.date.between(start_date, end_date))
            return session.exec(statement).all()

    def get_best_run(self) -> Optional[Run]:
        with self.session() as session:
            statement = select(Run).where(Run.distance > 0)
            runs = session.exec(statement).all()
            if not runs:
                return None
            return min(runs, key=lambda run: run.duration / run.distance)
