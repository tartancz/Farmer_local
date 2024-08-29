import pytest

from script.migrate import migrate
from src.database import Database
from src.farmer_local import FarmerLocal
from src.logger import add_loging_level, DISCORD_LEVEL
from test.mocks.cloud_mock import mock_modal
from test.mocks.redeemer_mock import RedeemerMock


@pytest.fixture(scope="function")
def farmer(tmp_path_factory) -> FarmerLocal:
    # TODO make watcher mocked...
    db = str(tmp_path_factory.mktemp('db') / "farmer.db")
    migrate(db)
    f = FarmerLocal(
        watcher=None,
        redeemer=RedeemerMock(),
        search_regex=r'123456789|5555',
        process_video_function=mock_modal,
        db=Database(db)
    )
    return f


@pytest.fixture(scope="session", autouse=True)
def set_logging():
    add_loging_level("DISCORD", DISCORD_LEVEL)
