"""
Database engine & session setup.

Uses SQLite by default (zero-config, file-based — perfect for this
assignment) but is Postgres-ready: just set the DATABASE_URL environment
variable to a Postgres connection string, e.g.

    export DATABASE_URL="postgresql://user:password@localhost:5432/webhooks"

and everything else (models, queries) works unchanged since we go through
SQLAlchemy's ORM rather than raw SQLite-specific SQL.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./payments.db")

# `check_same_thread` is only needed for SQLite (FastAPI uses multiple
# threads for a single request under the hood). It's ignored by other
# database backends.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
