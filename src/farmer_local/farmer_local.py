from datetime import datetime
import logging
import random
import re
from pathlib import Path
from time import sleep, time
from typing import TYPE_CHECKING

from src.logger import LOGGER_NAME
from src.video_processor.video_processor import VideoProcessor

if TYPE_CHECKING:
    from src.cloud_types import CodeType
    from src.database import Database
    from src.redeemer import Redeemer
    from src.watcher import Watcher
    from src.watcher.youtube_api import DetailedVideoFromApi

logger = logging.getLogger(LOGGER_NAME)


class FarmerLocal:
    def __init__(
        self,
        watcher: "Watcher",
        redeemer: "Redeemer",
        db: "Database",
        vp: "VideoProcessor",
        search_regex: str,
        skip_videos: bool = False,
    ):
        self.watcher = watcher
        self.redeemer = redeemer
        self.db = db
        self.vp = vp
        self.search_regex = re.compile(search_regex)
        self._start: float | None = None
        self.skip_videos = skip_videos

    def run(self):
        failures = list()
        while True:
            try:
                logger.discord("Starting Farmer Local")
                self._run()
            except Exception as e:
                logger.exception(e)
            finally:
                self.vp.downwarm_processor()
            # if more then 5 failures in time windows program will end
            failures.append(time())
            if len(failures) < 5:
                continue
            oldest_exc = failures.pop(0)
            if time() - oldest_exc < 1800:
                logger.discord("Program ended because too many exceptions occured")
                # sleep so logging can happened
                sleep(3)
                exit(1)

    def _run(self):
        self.watcher.insert_latest_videos_into_db()
        for video in self.watcher.watch(self.vp.prewarm_processor):
            if self.skip_videos and datetime.now().hour > 7 and datetime.now().hour < 22 and random.random() > 0.4:
                self.vp.downwarm_processor()
                continue
            self.process_video(video)
            self.vp.downwarm_processor()

    def process_video(self, video: "DetailedVideoFromApi"):
        logger.info(f"Going to process video {video.title}")
        with self:
            codes = self._finds_code_in_description(video)
            if codes:
                self._redeem_codes_from_description(codes, video)
            if TYPE_CHECKING:
                # only for type hint
                code_dict: CodeType  # type: ignore
            logger.info("Processing video with remote_gen")
            for code_dict in self.vp.get_codes(video):
                try:
                    self._redeem_codes_from_modal([code_dict], video)
                except Exception as E:
                    logger.error(E)
            logger.discord(
                f"Video {video.title} processed successfully and took: {time() - self._start}"
            )

    def _finds_code_in_description(self, video) -> list["str"]:
        codes = []
        logger.debug(f"trying to find codes in description")
        for code in self.search_regex.findall(video.description):
            logger.info(f"code was found in description: {code}")
            codes.append(code)
        if not codes:
            logger.debug(f"could not find code in description: {video.description}")
        return codes

    def _redeem_codes_from_modal(
        self, codes: list["CodeType"], video: "DetailedVideoFromApi"
    ):
        for code_dict in codes:
            code = code_dict["code"]
            code_state = self.redeemer.redeem_code(code)
            logger.discord(
                f"WOLT returned codeState {code_state.name} \n with code {code} \n using videoProcessing \n and took: {(time() - self._start):.2F} \n and timestamp: {code_dict['timestamp']:.2F} \n"
            )
            # write image from modal
            p = Path(f"./temp/{video.video_id}")
            p.mkdir(exist_ok=True, parents=True)
            p = p / f"{code_dict['code']}.jpg"
            p.write_bytes(code_dict["frame"])

            logger.info(f"saving image of code to {p.absolute()}")

            # inserting into db
            self.db.code.insert(
                video_id=video.video_id,
                code=code_dict.get("code"),
                timestamp=code_dict["timestamp"],
                how_long_to_process_in_total=time() - self._start,
                code_state_id=code_state.value,
                path_to_frame=str(p.absolute()),
            )

    def _redeem_codes_from_description(
        self, codes: list[str], video: "DetailedVideoFromApi"
    ):
        for code in codes:
            code_state = self.redeemer.redeem_code(code)
            logger.discord(
                f"WOLT returned codeState {code_state.name} with code {code} from description and took: {time() - self._start}"
            )
            # inserting into db
            self.db.code.insert(
                video_id=video.video_id,
                code=code,
                how_long_to_process_in_total=time() - self._start,
                code_state_id=code_state.value,
            )

    def __enter__(self):
        self._start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._start = None
