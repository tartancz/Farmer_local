from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection
    from src.database.database import Transaction


class Model:
    def __init__(self, db: 'Connection', transaction: 'Transaction'):
        self._db = db
        self._cursor = db.cursor()
        self._transaction = transaction

    def run_sql(self, sql: str, *args):
        self._cursor.execute(sql, *args)

    def run_sql_and_commit(self, sql: str, *args):
        self.run_sql(sql, *args)
        if not self._transaction.running_transaction:
            self._db.commit()

