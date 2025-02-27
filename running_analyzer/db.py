from decouple import config
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional
from running_analyzer.models import Run
from datetime import datetime


class Database:
    def __init__(self):
        self.DATABASE_URL = config("DATABASE_URL")
        self.ECHO = config("ECHO", default=False, cast=bool)
        self.engine = create_engine(self.DATABASE_URL, echo=self.ECHO)

    def get_engine(self):
        return self.engine

    def get_session(self):
        return Session(self.engine)

    def init_db(self):
        SQLModel.metadata.create_all(self.engine)


class RunRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_run_by_id(self, run_id: int) -> Optional[Run]:
        with self.db.get_session() as session:
            return session.get(Run, run_id)

    def list_runs(self) -> list[Run]:
        with self.db.get_session() as session:
            statement = select(Run)
            return session.exec(statement).all()

    def add_run(self, run: Run) -> Run:
        with self.db.get_session() as session:
            session.add(Run)
            session.commit()
            session.refresh(run)
            return run

    def delete_run(self, run_id: int) -> bool:
        with self.db.get_session() as session:
            run = session.get_run_by_id(run_id)
            if run:
                session.delete(run)
                session.commit()
                return True
            return False

    def update_run(self, run: Run, **kwargs) -> None:
        with self.db.get_session() as session:
            for key, value in kwargs.items():
                setattr(run, key, value)
            session.add(run)
            session.commit()

    def list_runs_by_type(self, run_type: str) -> list[Run]:
        with self.db.get_session() as session:
            statement = select(Run).where(Run.run_type == run_type)
            return session.exec(statement).all()

    def list_runs_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Run]:
        with self.db.get_session() as session:
            statement = select(Run).where(Run.date.between(start_date, end_date))
            return session.exec(statement).all()

    def get_best_run(self) -> Optional[Run]:
        with self.db.get_session() as session:
            statement = select(Run).where(Run.distance > 0)
            runs = session.exec(statement).all()
            if not runs:
                return None
            return min(runs, key=lambda run: run.duration / run.distance)
