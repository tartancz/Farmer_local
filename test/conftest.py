from pathlib import Path
from datetime import datetime
import pytest

from src.farmer_local import FarmerLocal
from src.database.database import Database


from test.mocks.redeemer_mock import RedeemerMock
from test.mocks.cloud_mock import mock_modal

from script.migrate import migrate
@pytest.fixture(scope='session')
def farmer(tmp_path_factory) -> FarmerLocal:
    # TODO make watcher mocked...
    db = str(tmp_path_factory.mktemp('db') / "farmer.db")
    migrate(db)
    f = FarmerLocal(
        watcher=None,
        redeemer=RedeemerMock(),
        search_regex=r'123456789|5555',
        fn=mock_modal,
        db=Database(db)
    )
    return f