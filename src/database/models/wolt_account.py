from dataclasses import dataclass
from datetime import datetime

from src.database.errors import RowDontExistException
from src.database.model import Model


@dataclass
class WoltAccount:
    id: int
    account_name: str
    created: datetime
    max_credits_per_month: int = 0
    priority: int = None
    working_credentials: bool | None = None


class WoltAccountModel(Model):
    def insert(self, account_name: str) -> int:
        insert_query = '''
            INSERT INTO wolt_account (account_name)
            VALUES (?);
        '''
        self.run_sql_and_commit(insert_query, [account_name])

        return self._cursor.lastrowid  # type: ignore

    def get_by_id(self, account_id: int) -> WoltAccount:
        select_query = '''
            SELECT id, account_name, created, max_credits_per_month, priority, working_credentials 
            FROM wolt_account
            WHERE id = ?
            LIMIT 1;
        '''
        self.run_sql(select_query, [account_id])
        account_row = self._cursor.fetchone()
        if not account_row:
            raise RowDontExistException(f"WoltAccount with video_id {account_id} do not exist")
        return WoltAccount(*account_row)

    def get_by_account_name(self, account_name: str) -> WoltAccount:
        select_query = '''
            SELECT id, account_name, created, max_credits_per_month, priority, working_credentials 
            FROM wolt_account
            WHERE account_name=?
            LIMIT 1;
        '''
        self.run_sql(select_query, [account_name])
        account_row = self._cursor.fetchone()
        if not account_row:
            raise RowDontExistException(f"WoltAccount with account_name {account_name} do not exist")
        return WoltAccount(*account_row)

    def get_credits_this_month(self, account_id: int) -> int:
        select_query = '''
            SELECT SUM(value)
            FROM code
            WHERE account_id = ? AND activated_at >= datetime('now', 'start of month');
        '''
        self.run_sql(select_query, [account_id])
        return self._cursor.fetchone()[0] or 0

    def get_user_for_redeem(self):
        select_query = '''
            SELECT id, account_name, created, max_credits_per_month, priority, working_credentials
            FROM wolt_account
            WHERE 
            priority IS NOT NULL 
            AND 
            wolt_account.max_credits_per_month < IFNULL((select SUM(c.value) FROM code c WHERE c.activated_by=wolt_account.account_name AND c.created >= datetime('now', 'start of month')), 0)
            AND
            (wolt_account.working_credentials = TRUE OR wolt_account.working_credentials IS NULL)
            ORDER BY priority 
            LIMIT 1
        '''
        self.run_sql(select_query)
        account_row = self._cursor.fetchone()
        if account_row:
            return WoltAccount(*account_row)
        select_query = '''
            SELECT id, account_name, created, max_credits_per_month, priority, working_credentials 
            FROM wolt_account
            WHERE 
            priority IS NOT NULL AND (wolt_account.working_credentials = TRUE OR wolt_account.working_credentials IS NULL)
            ORDER BY priority
            LIMIT 1
        '''
        self.run_sql(select_query)
        account_row = self._cursor.fetchone()
        if account_row:
            return WoltAccount(*account_row)
        raise RowDontExistException("No account available for redeeming")
