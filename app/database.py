from collections.abc import Generator
from pathlib import Path

from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_DIRECTORY / "data"
DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATA_DIRECTORY / "studyflow.db"
DATABASE_URL = URL.create("sqlite", database=str(DATABASE_PATH))

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(connection, _connection_record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class shared by SQLAlchemy models and Alembic metadata."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for one request, then close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
