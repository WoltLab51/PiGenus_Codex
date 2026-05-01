from __future__ import annotations

import argparse
import sys

from pigenus.core.config import Settings
from pigenus.db.session import init_db
from pigenus.services.maintenance import create_sqlite_backup, restore_sqlite_backup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pigenus-admin")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("init-db", help="Initialize database tables.")
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
