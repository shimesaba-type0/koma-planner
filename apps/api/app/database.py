import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401


DATABASE_URL = os.getenv("KOMA_DATABASE_URL", "sqlite:///./koma-planner.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables(db_engine=engine) -> None:
    SQLModel.metadata.create_all(db_engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
