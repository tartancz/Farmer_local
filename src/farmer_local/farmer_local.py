import logging
import re
from dataclasses import dataclass
from time import time, sleep
from pathlib import Path
import os

import requests

from typing import TYPE_CHECKING, TypedDict

from src.redeemer.redeemer import CodeState

if TYPE_CHECKING:
    from src.watcher.youtube_api.youtube_api import DetailedVideoFromApi
    from src.watcher.watcher import Watcher
    from src.database import Database
    from src.redeemer import Redeemer
    from src.cloud_types import CodeType
    from modal.functions import Function


logger = logging.getLogger("main")




class FarmerLocal:
    def __init__(self,
                 watcher: 'Watcher',
                 redeemer: 'Redeemer',
                 db: 'Database',
                 fn: 'Function',
                 search_regex: str
                 ):
        self.watcher = watcher
        self.redeemer = redeemer
        self.db = db
        self.fn = fn
        self.search_regex = re.compile(search_regex)
        self._start: float | None = None

    def run(self):
        failures = list()
        while True:
            try:
                self._run()
            except requests.exceptions.ConnectionError:
                # when internet connection is lost, will start pinging to google.com until response come successfully back
                logger.info(f"Not connection to internet")
                while True:
                    try:
                        requests.get("https://www.google.com")
                    except Exception:
                        sleep(10)
                        continue
                    break
            except Exception as e:
                # any other is logged
                logger.exception(e)
                print(e)
            # if more then 5 failures in time windows program will end
            failures.append(time())
            if len(failures) < 5:
                continue
            oldest_exc = failures.pop(0)
            if time() - oldest_exc < 1800:
                logger.critical(f"PROGRAM ENDING BECAUSE TOO MANY EXCEPTIONS OCCURED.")

    def __fake_return_video(self, video: str):
        video = self.watcher._yt_api.get_detailed_video(video)
        yield video

    def _run(self):
        self.watcher.insert_latest_videos_into_db()
        logger.info("starting farming")
        for video in self.watcher.watch():
            logger.info(f"Going to process video with id {video.video_id}")
            with self:
                codes = self._finds_code_in_desription(video)
                if codes:
                    logger.info(f"Found codes in description: {codes}")
                    self._redeem_codes_from_description(codes, video)
                if TYPE_CHECKING:
                    # only for type hint
                    code_dict: CodeType  # type: ignore
                logger.debug("Going to process video with OCR")
                for code_dict in self.fn.remote_gen(video.video_id):
                    print("asd", code_dict)
                    logger.debug(f"Found code in video: {video.video_id}, with timestamp {code_dict['timestamp']}")
                    self._redeem_codes_from_modal([code_dict], video)

    def _finds_code_in_desription(self, video) -> list['str']:
        codes = []
        for code in self.search_regex.findall(video.description):
            codes.append(code)
        return codes

    def _redeem_codes_from_modal(self, codes: list['CodeType'], video: 'DetailedVideoFromApi'):
        for code_dict in codes:
            code = code_dict["code"]
            code_state = self.redeemer.redeem_code(code)
            logger.info(f"Code returned {code_state.name} with code {code_dict['code']}")
            # TODO how long took from running ocr modal

            # write image from modal
            p = Path(f"./temp/{video.video_id}")
            p.mkdir(exist_ok=True, parents=True)
            p = p / f"{code_dict['code']}.jpg"
            p.write_bytes(code_dict["frame"])

            #inserting into db
            self.db.code.insert(
                video_id=video.video_id,
                code=code_dict.get("code"),
                timestamp=code_dict["timestamp"],
                how_long_to_proccess_in_total=time() - self._start,
                code_state_id=code_state.value,
                path_to_frame=p.absolute()
            )

    def _redeem_codes_from_description(self, codes: list[str], video: 'DetailedVideoFromApi'):
        for code in codes:
            code_state = self.redeemer.redeem_code(code)
            logger.info(f"Code returned {code_state.name} with code {code}")

            # inserting into db
            self.db.code.insert(
                video_id=video.video_id,
                code=code,
                how_long_to_proccess_in_total=time() - self._start,
                code_state_id=code_state.value
            )

    def __enter__(self):
        self._start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._start = None
