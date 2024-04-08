import logging
import os
import sqlite3
from time import sleep

from src.watcher.youtube_api import YoutubeApi, DetailedVideoFromApi
from src.database import Database

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator

SECONDS_IN_DAY = 60 * 60 * 24
logger = logging.getLogger(__name__)


class Watcher:
    def __init__(self,
                 youtube_api: YoutubeApi,
                 db: Database,
                 maximum_retries: int = 10,
                 sleep_time: int = 10,
                 ):
        self._yt_api = youtube_api
        self._db = db
        self.maximum_retries = maximum_retries
        self.sleep_time = sleep_time
        self._video_count = 0

    def watch(self) -> 'Generator[DetailedVideoFromApi, None, None]':
        '''
        will return new video when someone will upload it
        :return:
        '''
        self._video_count = self._yt_api.get_video_count()
        while True:
            sleep(SECONDS_IN_DAY / self._yt_api.maximum_checks_calls_per_day)
            if self._is_video_count_changed():
                video = self._get_latest_video()
                if video:
                    logger.info(f"New video found with video_id: {video.video_id}")
                    self._db.youtube_video.insert(
                        video_id=video.video_id,
                        channel_id=self._yt_api.channel_id,
                        description=video.description,
                        publish_time=video.publish_time,
                        title=video.title,
                        video_length=video.video_lenght,
                        url=video.url,
                        skipped_finding=False,
                    )
                    yield video

    def insert_latest_videos_into_db(self):
        for video in self._yt_api.get_latest_videos_from_api(10):
            try:
                self._db.youtube_video.insert(
                    video_id=video.video_id,
                    channel_id=self._yt_api.channel_id,
                    publish_time=video.publish_time,
                    title=video.title,
                    url=video.url,
                    skipped_finding=True,
                )
            except sqlite3.IntegrityError:
                pass

    def _is_video_count_changed(self):
        actual_video_count = self._yt_api.get_video_count()
        # if youtuber delete video
        if actual_video_count < self._video_count:
            logger.info("video count has decreased")
            self._video_count = actual_video_count
            return False

        # new video
        if actual_video_count != self._video_count:
            logger.info(f"video count has changed from {self._video_count} to {actual_video_count}")
            self._video_count = actual_video_count
            return True
        return False

    def _get_latest_video(self) -> DetailedVideoFromApi | None:
        for _ in range(self.maximum_retries):
            video_api = self._yt_api.get_latest_videos_from_api(1)[0]
            if not self._db.youtube_video.is_video_in_db(video_id=video_api.video_id):
                return self._yt_api.get_detailed_video(video_id=video_api.video_id)
            video_scrapping_id = self._yt_api.get_latest_videos_from_scrapping(1)[0]
            if not self._db.youtube_video.is_video_in_db(video_id=video_scrapping_id):
                return self._yt_api.get_detailed_video(video_id=video_scrapping_id)
            sleep(self.sleep_time)
        return None
