from src.database import Database
from src.farmer_local.farmer_local import FarmerLocal
from src.logger import configure_loggers
from src.redeemer.wolt import Wolt
from src.setting import (
    YOUTUBE_API_KEY,
    YOUTUBE_CHANNEL_ID,
    YOUTUBE_CHANNEL_NAME,
    MODAL_PROCESS_FUNCTION_NAME,
    MODAL_PROCESS_DOWNLOAD_NAME,
    MODAL_APP_NAME,
    WOLT_NAME,
    DATABASE_CONNECTION_STRING
)
from src.video_processor.cloud_vp import ModalVP
from src.watcher.watcher import Watcher
from src.watcher.youtube_api import YoutubeApi


def farm():
    db = Database(DATABASE_CONNECTION_STRING)
    watcher = Watcher(
        youtube_api=YoutubeApi(api_key=YOUTUBE_API_KEY,
                               channel_name=YOUTUBE_CHANNEL_NAME,
                               channel_id=YOUTUBE_CHANNEL_ID),
        db=db,
    )
    wolt = Wolt(db, WOLT_NAME)

    f = FarmerLocal(
        watcher=watcher,
        redeemer=wolt,
        db=db,
        vp=ModalVP(MODAL_APP_NAME, MODAL_PROCESS_FUNCTION_NAME, MODAL_PROCESS_DOWNLOAD_NAME),
        search_regex="AG[1-9][0|O]{2}[1-9A-z]{7}"
    )
    f.run()


def main():
    configure_loggers()
    farm()


if __name__ == "__main__":
    main()
