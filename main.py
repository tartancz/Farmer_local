from src.database import Database
from src.farmer_local.farmer_local import FarmerLocal
from src.logger import configure_loggers
from src.redeemer.wolt import Redeemer, Wolt
from src.setting import (
    DATABASE_CONNECTION_STRING,
    MODAL_APP_NAME,
    MODAL_PROCESS_DOWNLOAD_NAME,
    MODAL_PROCESS_FUNCTION_NAME,
    WOLT_NAME,
    YOUTUBE_API_KEY,
    YOUTUBE_CHANNEL_ID,
    YOUTUBE_CHANNEL_NAME,
)
from src.video_processor import ModalVP, VideoProcessor
from src.watcher.watcher import Watcher
from src.watcher.youtube_api import YoutubeApi


def get_farmer(
    db: Database | None = None,
    watcher: Watcher | None = None,
    redeemer: Redeemer | None = None,
    vp: VideoProcessor | None = None,
    search_regex="AG[1-9][0|O]{2}[1-9A-z]{7}",
):
    if db is None:
        db = Database(DATABASE_CONNECTION_STRING)

    if watcher is None:
        watcher = Watcher(
            youtube_api=YoutubeApi(
                api_key=YOUTUBE_API_KEY,
                channel_name=YOUTUBE_CHANNEL_NAME,
                channel_id=YOUTUBE_CHANNEL_ID,
            ),
            db=db,
        )

    if redeemer is None:
        redeemer = Wolt(db, WOLT_NAME)

    if vp is None:
        vp = ModalVP(
            MODAL_APP_NAME, MODAL_PROCESS_FUNCTION_NAME, MODAL_PROCESS_DOWNLOAD_NAME
        )

    f = FarmerLocal(
        watcher=watcher, redeemer=redeemer, db=db, vp=vp, search_regex=search_regex
    )
    return f


def main():
    configure_loggers()
    get_farmer().run()


if __name__ == "__main__":
    main()
