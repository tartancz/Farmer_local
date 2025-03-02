from dataclasses import dataclass
from datetime import datetime

from src.database.errors import RowDontExistException
from src.database.model import Model


@dataclass
class WoltAccount:
    id: int
    account_name: str
    created: datetime


class WoltAccountModel(Model):
    def insert(self, account_name: str) -> int:
        insert_query = """
            INSERT INTO wolt_account (account_name)
            VALUES (?);
        """
        self.run_sql_and_commit(insert_query, [account_name])

        return self._cursor.lastrowid  # type: ignore

    def get_by_id(self, account_id: int) -> WoltAccount:
        select_query = """
            SELECT id, account_name, created
            FROM wolt_account
            WHERE id = ?
            LIMIT 1;
        """
        self.run_sql(select_query, [account_id])
        account_row = self._cursor.fetchone()
        if not account_row:
            raise RowDontExistException(
                f"WoltAccount with video_id {account_id} do not exist"
            )
        return WoltAccount(*account_row)

    def get_by_account_name(self, account_name: str) -> WoltAccount:
        select_query = """
            SELECT id, account_name, created
            FROM wolt_account
            WHERE account_name=?
            LIMIT 1;
        """
        self.run_sql(select_query, [account_name])
        account_row = self._cursor.fetchone()
        if not account_row:
            raise RowDontExistException(
                f"WoltAccount with account_name {account_name} do not exist"
            )
        return WoltAccount(*account_row)
