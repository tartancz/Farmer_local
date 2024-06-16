import argparse
import sqlite3
from pathlib import Path

MIGRATION_SCRIPTS_FOLDER = Path(__file__).parent.parent / "src" / "database" / "migration" / "_migration"


def migrate(conn_str: str):
    version = _get_actual_version(conn_str)
    conn = sqlite3.connect(conn_str)
    cur = conn.cursor()
    while True:
        version = _get_next_version(version)
        actual_migration = MIGRATION_SCRIPTS_FOLDER / f"{version}.sql"
        if not actual_migration.exists():
            break
        with open(actual_migration, "r") as f:
            cur.executescript(f.read())
        conn.commit()
        print(f"Migration {version} was applied.")


def _get_next_version(actual_version: str):
    return "{:04}".format(int(actual_version) + 1)


def _get_actual_version(conn_str: str):
    try:
        SQL = 'SELECT VERSION from database_version '
        with sqlite3.connect(conn_str) as conn:
            cur = conn.cursor()
            cur.execute(SQL)
            return cur.fetchone()[0]
    except Exception:
        return '0000'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="migration",
        description="Create migration for app"
    )
    parser.add_argument("conn_str", help="Connection string to database.", type=str)
    args = parser.parse_args()
    migrate(args.conn_str)
