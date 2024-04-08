import sqlite3

from src.database.models import WoltAccountModel, WoltTokenModel, YoutubeVideoModel
from dataclasses import dataclass

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from sqlite3 import Connection
    from src.database.model import Model

    model_generic = TypeVar('model_generic', bound='Model')


class Transaction:
    def __init__(self, db: 'Connection'):
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
        self.wolt_account = self._init_model(WoltAccountModel)
        self.wolt_token = self._init_model(WoltTokenModel)
        self.youtube_video = self._init_model(YoutubeVideoModel)

    def _init_model(self, model: type['model_generic']) -> 'model_generic':
        return model(self._db, self.transaction)
