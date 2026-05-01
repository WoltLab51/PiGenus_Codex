from __future__ import annotations

from sqlalchemy import Column, Engine, Integer, MetaData, String, Table, insert, select
from sqlalchemy.orm import Session

SCHEMA_KEY = "schema"
CURRENT_SCHEMA_VERSION = 1


def schema_version_table(metadata: MetaData) -> Table:
    return Table(
        "schema_version",
        metadata,
        Column("key", String(80), primary_key=True),
        Column("version", Integer, nullable=False),
    )


def migrate_database(engine: Engine) -> int:
    from pigenus.db.session import Base
    from pigenus.db import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)
    metadata = MetaData()
    version_table = schema_version_table(metadata)
    metadata.create_all(bind=engine)
    with Session(engine) as session:
        current = session.scalar(
            select(version_table.c.version).where(version_table.c.key == SCHEMA_KEY)
        )
        if current is None:
            session.execute(
                insert(version_table).values(key=SCHEMA_KEY, version=CURRENT_SCHEMA_VERSION)
            )
            session.commit()
            return CURRENT_SCHEMA_VERSION
        if current > CURRENT_SCHEMA_VERSION:
            raise RuntimeError(
                f"database schema version {current} is newer than supported "
                f"version {CURRENT_SCHEMA_VERSION}"
            )
        if current < CURRENT_SCHEMA_VERSION:
            _run_upgrade_steps(session, version_table, current, CURRENT_SCHEMA_VERSION)
            session.commit()
        return CURRENT_SCHEMA_VERSION


def get_schema_version(engine: Engine) -> int | None:
    metadata = MetaData()
    version_table = schema_version_table(metadata)
    metadata.create_all(bind=engine)
    with Session(engine) as session:
        return session.scalar(select(version_table.c.version).where(version_table.c.key == SCHEMA_KEY))


def _run_upgrade_steps(
    session: Session,
    version_table: Table,
    current: int,
    target: int,
) -> None:
    version = current
    while version < target:
        version += 1
        session.execute(
            version_table.update()
            .where(version_table.c.key == SCHEMA_KEY)
            .values(version=version)
        )
