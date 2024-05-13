import logging
import re
from pathlib import Path
from time import time, sleep
from typing import TYPE_CHECKING, Callable, Generator

import requests

from src.logger import LOGGER_NAME

if TYPE_CHECKING:
    from src.watcher.youtube_api import DetailedVideoFromApi
    from src.watcher import Watcher
    from src.database import Database
    from src.redeemer import Redeemer
    from src.cloud_types import CodeType
    from modal.functions import Function

logger = logging.getLogger(LOGGER_NAME)


class FarmerLocal:
    def __init__(self,
                 watcher: 'Watcher',
                 redeemer: 'Redeemer',
                 db: 'Database',
                 process_video_function: Callable[['DetailedVideoFromApi'], Generator['CodeType', None, None]],
                 search_regex: str
                 ):
        self.watcher = watcher
        self.redeemer = redeemer
        self.db = db
        self.process_video_function = process_video_function
        self.search_regex = re.compile(search_regex)
        self._start: float | None = None

    def run(self):
        failures = list()
        while True:
            try:
                logger.discord("Starting Farmer Local")
                self._run()
            except Exception as e:
                logger.error(e)
                while True:
                    # when internet connection is lost, will start pinging to google.com until response come successfully back
                    try:
                        requests.get("https://www.google.com")
                    except Exception as innerE:
                        sleep(10)
                        logger.debug("still no internet connection")
                        continue
                    logger.info("internet connection established")
                    break
            # if more then 5 failures in time windows program will end
            failures.append(time())
            if len(failures) < 5:
                continue
            oldest_exc = failures.pop(0)
            if time() - oldest_exc < 1800:
                logger.discord("Program ended because too many exceptions occured")
                exit(1)

    def _run(self):
        self.watcher.insert_latest_videos_into_db()
        for video in self.watcher.watch():
            self.process_video(video)

    def process_video(self, video: 'DetailedVideoFromApi'):
        logger.info(f"Going to process video {video.title}")
        with self:
            codes = self._finds_code_in_description(video)
            if codes:
                self._redeem_codes_from_description(codes, video)
            if TYPE_CHECKING:
                # only for type hint
                code_dict: CodeType  # type: ignore
            logger.info("Processing video with remote_gen")
            for code_dict in self.process_video_function(video):
                try:
                    self._redeem_codes_from_modal([code_dict], video)
                except Exception as E:
                    logger.error(E)

    def _finds_code_in_description(self, video) -> list['str']:
        codes = []
        logger.debug(f"trying to find codes in description")
        for code in self.search_regex.findall(video.description):
            logger.info(f"code was found in description: {code}")
            codes.append(code)
        if not codes:
            logger.debug(f"could not find code in description: {video.description}")
        return codes

    def _redeem_codes_from_modal(self, codes: list['CodeType'], video: 'DetailedVideoFromApi'):
        for code_dict in codes:
            code = code_dict["code"]
            code_state = self.redeemer.redeem_code(code)
            logger.discord(f"WOLT returned codeState {code_state.name} with code {code} using videoProcessing")
            # TODO how long took from running ocr modal

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
                path_to_frame=str(p.absolute())
            )

    def _redeem_codes_from_description(self, codes: list[str], video: 'DetailedVideoFromApi'):
        for code in codes:
            code_state = self.redeemer.redeem_code(code)
            logger.discord(f"WOLT returned codeState {code_state.name} with code {code} from description")
            # inserting into db
            self.db.code.insert(
                video_id=video.video_id,
                code=code,
                how_long_to_process_in_total=time() - self._start,
                code_state_id=code_state.value
            )

    def __enter__(self):
        self._start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._start = None
