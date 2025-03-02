import logging
import sqlite3
from time import sleep
from typing import TYPE_CHECKING, Callable

from src.database import Database
from src.logger import LOGGER_NAME
from src.watcher.youtube_api import DetailedVideoFromApi, YoutubeApi

if TYPE_CHECKING:
    from typing import Generator

SECONDS_IN_DAY = 60 * 60 * 24

logger = logging.getLogger(LOGGER_NAME)


class Watcher:
    def __init__(
        self,
        youtube_api: YoutubeApi,
        db: Database,
        maximum_retries: int = 10,
        sleep_time: int = 10,
    ):
        self.yt_api = youtube_api
        self._db = db
        self.maximum_retries = maximum_retries
        self.sleep_time = sleep_time
        self._video_count = 0

    def watch(
        self, cb_video_changed: Callable
    ) -> "Generator[DetailedVideoFromApi, None, None]":
        """
        will return new video when someone will upload it
        :return:
        """
        logger.info("going to watch for new video")
        self._video_count = self.yt_api.get_video_count()
        while True:
            sleep(SECONDS_IN_DAY / self.yt_api.maximum_checks_calls_per_day)
            if self._is_video_count_changed():
                cb_video_changed()
                video = self._get_latest_video()
                if video:
                    logger.info(
                        f"inserting video into db id: {video.video_id} and title: {video.title}"
                    )
                    self._db.youtube_video.insert(
                        video_id=video.video_id,
                        channel_id=self.yt_api.channel_id,
                        description=video.description,
                        publish_time=video.publish_time,
                        title=video.title,
                        video_length=video.video_lenght,
                        url=video.url,
                        skipped_finding=False,
                    )
                    yield video

    def insert_latest_videos_into_db(self):
        logger.info("Inserting latest videos into database")
        for video in self.yt_api.get_latest_videos_from_api(10):
            try:
                self._db.youtube_video.insert(
                    video_id=video.video_id,
                    channel_id=self.yt_api.channel_id,
                    publish_time=video.publish_time,
                    title=video.title,
                    url=video.url,
                    skipped_finding=True,
                )
                logger.debug(f"Inserted video {video.video_id}")
            except sqlite3.IntegrityError:
                pass

    def _is_video_count_changed(self):
        actual_video_count = self.yt_api.get_video_count()
        # if youtuber delete video
        if actual_video_count < self._video_count:
            logger.discord(
                f"video count has decreased from {self._video_count} to {actual_video_count}"
            )
            self._video_count = actual_video_count
            return False

        # new video
        if actual_video_count != self._video_count:
            logger.discord(
                f"NEW VIDEO. from {self._video_count} to {actual_video_count}"
            )
            self._video_count = actual_video_count
            return True
        return False

    def _get_latest_video(self) -> DetailedVideoFromApi | None:
        logger.info("Getting latest video from API")
        for _ in range(self.maximum_retries):
            video_api = self.yt_api.get_latest_videos_from_api(1)[0]
            logger.info(f"API returned {video_api.video_id} as last video")
            if not self._db.youtube_video.is_video_in_db(video_id=video_api.video_id):
                logger.discord(
                    f"NEW VIDEO FROM API WAS FOUND! id: {video_api.video_id}"
                )
                return self.yt_api.get_detailed_video(video_id=video_api.video_id)
            SCRAPING_TRIES = 5
            for _ in range(SCRAPING_TRIES):
                video_scrapping_id = self.yt_api.get_latest_videos_from_scrapping(1)[0]
                logger.info(f"SCRAPING returned {video_api.video_id} as last video")
                if not self._db.youtube_video.is_video_in_db(
                    video_id=video_scrapping_id
                ):
                    logger.discord(
                        f"NEW VIDEO FROM SCRAPING WAS FOUND! id: {video_scrapping_id}"
                    )
                    return self.yt_api.get_detailed_video(video_id=video_scrapping_id)
                logger.info(f"Video was not found going to sleep and try again")
                sleep(self.sleep_time / SCRAPING_TRIES)
        logger.discord(f"Video was NOT FOUND!")
        return None
