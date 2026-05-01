from __future__ import annotations

import argparse
import sys

from pigenus.core.config import Settings
from pigenus.db.migrations import get_schema_version, migrate_database
from pigenus.db.session import build_engine, init_db
from pigenus.services.maintenance import create_sqlite_backup, restore_sqlite_backup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus-admin")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("init-db", help="Initialize database tables.")
    subcommands.add_parser("migrate", help="Run database migrations.")
    subcommands.add_parser("schema-version", help="Print the configured database schema version.")
    subcommands.add_parser("backup", help="Create a SQLite backup.")

    restore = subcommands.add_parser("restore", help="Restore SQLite database from backup.")
    restore.add_argument("backup_path")
    restore.add_argument("--yes", action="store_true", help="Confirm overwriting the configured database.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    if args.command == "init-db":
        init_db(settings)
        print("database initialized")
        return 0
    if args.command == "migrate":
        engine = build_engine(settings)
        version = migrate_database(engine)
        print(f"database migrated to schema version {version}")
        return 0
    if args.command == "schema-version":
        engine = build_engine(settings)
        version = get_schema_version(engine)
        print("uninitialized" if version is None else version)
        return 0
    if args.command == "backup":
        init_db(settings)
        backup_path = create_sqlite_backup(settings)
        if backup_path is None:
            print("backup skipped: configured database is not a file-backed SQLite database")
            return 1
        print(backup_path)
        return 0
    if args.command == "restore":
        if not args.yes:
            print("restore refuses to overwrite the database without --yes", file=sys.stderr)
            return 2
        restore_sqlite_backup(settings, args.backup_path)
        print("database restored")
        return 0
    return 2
