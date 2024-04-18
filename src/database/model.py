from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection
    from src.database.database import Transaction


class Model:
    def __init__(self, db: 'Connection', table_name: str, transaction: 'Transaction'):
        '''
        BE CAREFULL PARAMETER TABLE_NAME IS NOT SAFE FOR SQL INJECTION!!!
        '''
        self._db = db
        self._cursor = db.cursor()
        self.table_name = table_name
        self._transaction = transaction

    def run_sql(self, sql: str, *args):
        self._cursor.execute(sql, *args)

    def run_sql_and_commit(self, sql: str, *args):
        self.run_sql(sql, *args)
        if not self._transaction.running_transaction:
            self._db.commit()

    def run_and_fechall(self, sql: str, *args):
        self.run_sql(sql, *args)
        return self._cursor.fetchall()

    def get_count_of_rows(self):
        sql = f"SELECT COUNT(*) FROM {self.table_name};"
        return self._cursor.execute(sql).fetchone()[0]

