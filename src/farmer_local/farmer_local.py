import logging
import re
from dataclasses import dataclass
from time import time, sleep
from pathlib import Path

import requests

from typing import TYPE_CHECKING

from src.redeemer.redeemer import CodeState

if TYPE_CHECKING:
    from src.watcher.youtube_api.youtube_api import DetailedVideoFromApi
    from src.watcher.watcher import Watcher
    from src.database import Database
    from src.redeemer import Redeemer
    from modal.functions import Function

logger = logging.getLogger("main")


@dataclass
class Code:
    code: str
    how_long_to_proccess_in_total: float | None = None
    how_long_to_proccess_in_cloud: float | None = None
    timestamp: float | None = None
    frame: bytes | None = None


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
        self._start: int | None = None

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
                return

    def __fake_return_video(self, video: str):
        video = self.watcher._yt_api.get_detailed_video(video)
        yield video

    def _run(self):
        # self.watcher.insert_latest_videos_into_db()
        logger.info("starting farming")
        # for video in self.watcher.watch():
        for video in self.__fake_return_video("PctEhHUqnvY"):
            logger.debug(f"Going to process video with id {video.video_id}")
            with self:
                codes = self._finds_code_in_desription(video)
                if codes:
                    logger.info(f"Found codes in description: {codes}")
                    self._redeem_codes(codes)
                if TYPE_CHECKING:
                    # only for type hint
                    code_obj: Code  # type: ignore
                logger.debug("Going to process video with OCR")
                for code_obj in self.fn.remote_gen(video.video_id):
                    print("asd", code_obj)
                    code_obj.how_long_to_proccess_in_cloud = time() - self._start
                    logger.debug(f"Found code in video: {code_obj.code}, with timestamp {code_obj.timestamp}")
                    self._redeem_codes([code_obj])

    def _finds_code_in_desription(self, video) -> list[Code]:
        codes = []
        for code in self.search_regex.findall(video.description):
            code_obj = Code(
                code=code
            )
            codes.append(code_obj)
        return codes

    def _redeem_codes(self, codes: list[Code], video: 'DetailedVideoFromApi'):
        for code in codes:
            code_state = self.redeemer.redeem_code(code.code)
            logger.info(f"Code returned {code_state.name} with {code}")
            # TODO temporary solution add database row and better image saving
            logger.info(f"""
            Code: {code}
            Video: {video}
            CodeState: {code_state.name}
            timestamp: {code.timestamp}
            how_long_to_proccess_in_total: {time() - self._start}
            how_long_to_proccess_in_cloud: {code}
            """)
            if code.frame:
                p = Path(f"./temp/{video.video_id}")
                p.mkdir(exist_ok=True)
                with open(p / f"{code.code}.jpg", 'wb') as f:
                    f.write(code.frame)

    def __enter__(self):
        self._start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._start = None
