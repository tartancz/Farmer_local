from dataclasses import dataclass
import logging
import os
from datetime import datetime

from src.database.model import Model
from src.database.errors import RowDontExistException

logger = logging.getLogger(__name__)


@dataclass
class WoltAccount:
    id: int
    account_name: str
    created: datetime


class WoltAccountModel(Model):
    def insert(self, account_name: str) -> int:
        insert_query = '''
            INSERT INTO wolt_account (account_name)
            VALUES (?);
        '''
        logger.debug(f"inserting WoltAccount to db with account_name: {account_name}")
        self.run_sql_and_commit(insert_query, [account_name])

        return self._cursor.lastrowid  # type: ignore

    def get_by_id(self, account_id: int) -> WoltAccount:
        select_query = '''
            SELECT id, account_name, created
            FROM wolt_account
            WHERE id = ?
            LIMIT 1;
        '''
        logger.debug(f"getting WoltAccount by video_id: {account_id}")
        self.run_sql(select_query, [account_id])
        account_row = self._cursor.fetchone()
        if not account_row:
            logger.debug(f"WoltAccount with video_id {account_id} was not found")
            raise RowDontExistException(f"WoltAccount with video_id {account_id} do not exist")
        return WoltAccount(*account_row)

    def get_by_account_name(self, account_name: str) -> WoltAccount:
        select_query = '''
            SELECT id, account_name, created
            FROM wolt_account
            WHERE account_name=?
            LIMIT 1;
        '''
        logger.debug(f"getting WoltAccount by account_name: {account_name}")
        self.run_sql(select_query, [account_name])
        account_row = self._cursor.fetchone()
        if not account_row:
            logger.debug(f"WoltAccount with account_name {account_name} was not found")
            raise RowDontExistException(f"WoltAccount with account_name {account_name} do not exist")
        return WoltAccount(*account_row)
