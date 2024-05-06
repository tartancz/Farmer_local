import sqlite3
import sys
from pathlib import Path
import argparse

# Add the root of the project to the sys.path for case when scripts are runned from another directory
sys.path.append(str(Path(__file__).parent.parent))

from src.database.database import Database
from src.redeemer.errors import RefreshAuthFailedException

from src.redeemer.wolt import Wolt


def main(
        conn_str: str,
        account_name: str,
        refresh_token: str
):
    db = Database(conn_str)
    try:
        Wolt.create_new_account(db, account_name, refresh_token)
    except RefreshAuthFailedException:
        print("Refresh token is invalid.")
    except sqlite3.IntegrityError as e:
        if e.sqlite_errorcode == 2067:
            print("Account with this name already exists.")
        else:
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="create wolt account",
        description="will create wolt account in database."
    )
    parser.add_argument("conn_str", help="Connection string to database.", type=str)
    parser.add_argument("account_name", help="Account name for wolt account. (can be anything)", type=str)
    parser.add_argument("refresh_token", help="Refresh access_token for wolt account.", type=str)
    args = parser.parse_args()
    main(
        args.conn_str,
        args.account_name,
        args.refresh_token
    )