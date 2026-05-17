"""
SQLite engine and session management.

The database file lives at  <project_root>/data/rooted.db
so it is outside the Python package and easy to back up or reset.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

# Place the DB file two levels above this file: src/rooted_and_rising_crew/ → data/
_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DATA_DIR.mkdir(exist_ok=True)

_DB_PATH = _DATA_DIR / "rooted.db"

engine = create_engine(f"sqlite:///{_DB_PATH}", echo=False)


def create_db_and_tables() -> None:
    """Create all tables that do not already exist. Safe to call on every startup."""
    # Import here so all SQLModel table classes are registered before metadata.create_all
    from rooted_and_rising_crew.models.db import (  # noqa: F401
        ActivityItemRow,
        BookItemRow,
        FoodItemRow,
        JournalEntryRow,
        PlannedActivityRow,
        WeeklyPlanRow,
    )
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Yield a committed-on-exit session. Rolls back on exception."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
