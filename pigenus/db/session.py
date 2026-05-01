from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from pigenus.core.config import Settings


class Base(DeclarativeBase):
    pass


_engine = None
SessionLocal: sessionmaker[Session] | None = None


def build_engine(settings: Settings):
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    if settings.database_url == "sqlite://":
        return create_engine(
            settings.database_url,
            connect_args=connect_args,
            poolclass=StaticPool,
            future=True,
        )
    return create_engine(settings.database_url, connect_args=connect_args, future=True)


def init_db(settings: Settings) -> None:
    global _engine, SessionLocal
    sqlite_path = settings.sqlite_path
    if sqlite_path and sqlite_path.parent != sqlite_path:
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    _engine = build_engine(settings)
    SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    from pigenus.db.migrations import migrate_database

    migrate_database(_engine)


def get_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("database is not initialized")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
