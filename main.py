import time

from src.redeemer.wolt import Wolt
import modal

from src.watcher.youtube_api import YoutubeApi, DetailedVideoFromApi
from src.database import Database
from src.watcher.watcher import Watcher
import logging
from src.farmer_local.farmer_local import FarmerLocal


def setLogging():
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler("app.log")
    fh.setLevel(logging.DEBUG)
    fr = logging.Formatter(fmt='%(asctime)s : %(levelname)s : %(filename)s : %(message)s', datefmt="%m/%d/%Y %H:%M:%S")
    fh.setFormatter(fr)

    logger.addHandler(fh)

MUJ_YT = 'UCC_0FddrsldugADEZa8N-oA'
AG_YT = 'UCV_67Ju1MeHPOAF_oDv7OmA'

def farm():
    db = Database("db.db")
    watcher = Watcher(
        youtube_api=YoutubeApi(api_key="AIzaSyCzoYgSTthBWylfMy7-eIhQOwpN33reAc0",
                               channel_name='AgraelusReakce',
                               channel_id="UCV_67Ju1MeHPOAF_oDv7OmA"),
        db=db,
    )
    wolt = Wolt(db, "moje")
    fn = modal.Function.lookup("farming-wolt", "process_youtube_video")
    f = FarmerLocal(
        watcher=watcher,
        redeemer=wolt,
        db=db,
        fn=fn,
        search_regex="AG[1-9][0|O]{2}[1-9A-z]{7}"
    )
    f.run()


def main():
    setLogging()
    farm()


if __name__ == "__main__":
    main()
