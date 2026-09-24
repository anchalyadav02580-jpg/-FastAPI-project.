"""
Database configuration.

Sets up the SQLite engine and exposes a session dependency for routes.
"""

from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./events.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    """Create all tables registered on SQLModel's metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields one Session per request."""
    with Session(engine) as session:
        yield session
