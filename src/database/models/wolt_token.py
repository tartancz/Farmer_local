from dataclasses import dataclass
from datetime import datetime

from src.database.errors import RowDontExistException
from src.database.model import Model


@dataclass
class WoltToken:
    id: int
    account_id: int
    refresh_token: str
    access_token: str
    expires_in: int
    created: datetime


class WoltTokenModel(Model):
    def insert(self, account_id: int, refresh_token: str, access_token: str, expires_in: int = 1800) -> int:
        insert_query = '''
            INSERT INTO wolt_token (account_id, refresh_token, access_token, expires_in)
            VALUES (?, ?, ?, ?);
        '''
        self.run_sql_and_commit(insert_query, [account_id, refresh_token, access_token, expires_in])
        return self._cursor.lastrowid  # type: ignore

    def get_by_id(self, token_id: int) -> WoltToken:
        select_query = '''
            SELECT id, account_id, refresh_token, access_token, expires_in, created
            FROM wolt_token
            WHERE id = ?
            LIMIT 1;
        '''
        self._cursor.execute(select_query, [token_id])
        token_row = self._cursor.fetchone()
        if not token_row:
            raise RowDontExistException(f"WoltToken with video_id {token_id} do not exist")
        return WoltToken(*token_row)

    def get_latest_token(self, account_id: int) -> WoltToken:
        select_query = '''
            SELECT id, account_id, refresh_token, access_token, expires_in, created
            FROM wolt_token
            WHERE account_id = ?
            ORDER BY created DESC
            LIMIT 1;
        '''
        self._cursor.execute(select_query, [account_id])
        token_row = self._cursor.fetchone()
        if not token_row:
            raise RowDontExistException(f"WoltToken do not exist")
        return WoltToken(*token_row)
