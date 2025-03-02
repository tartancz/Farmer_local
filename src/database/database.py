import sqlite3
from typing import TYPE_CHECKING, TypeVar

from src.database.models import (
    CodeModel,
    WoltAccountModel,
    WoltTokenModel,
    YoutubeVideoModel,
)

if TYPE_CHECKING:
    from sqlite3 import Connection

    model_generic = TypeVar("model_generic", bound="Model")


class Transaction:
    def __init__(self, db: "Connection"):
        self.running_transaction: bool = False
        self._db = db

    def __enter__(self):
        self.running_transaction = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._db.rollback()
        else:
            self._db.commit()
        self.running_transaction = False

    def rollback(self):
        self._db.rollback()


class Database:
    def __init__(self, cnstr: str):
        self._db = sqlite3.connect(cnstr)
        self.transaction = Transaction(self._db)
        self.wolt_account = self._init_model(WoltAccountModel, "wolt_account")
        self.wolt_token = self._init_model(WoltTokenModel, "wolt_token")
        self.youtube_video = self._init_model(YoutubeVideoModel, "youtube_video")
        self.code = self._init_model(CodeModel, "code")

    def _init_model(
        self, model: type["model_generic"], table_name: str
    ) -> "model_generic":
        if not self.table_exists(table_name):
            raise ValueError(f"Table {table_name} does not exist, cannot create model")
        return model(self._db, table_name, self.transaction)

    def table_exists(self, table_name: str) -> bool:
        query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
        return self._db.execute(query, (table_name,)).fetchone() is not None
