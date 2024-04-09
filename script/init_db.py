import argparse
import sqlite3
from pathlib import Path


def migrate(conn_str: str):
    conn = sqlite3.connect(conn_str)
    cur = conn.cursor()
    migration_script_path = Path(__file__).parent.parent / "src" / "database" / "migration.sql"
    with open(migration_script_path, "r") as f:
        cur.executescript(f.read())
    conn.commit()
    print("Migration was applied.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="migration",
        description="Create migration for app"
    )
    parser.add_argument("conn_str", help="Connection string to database.", type=str)
    args = parser.parse_args()
    migrate(args.conn_str)