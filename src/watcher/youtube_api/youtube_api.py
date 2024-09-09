import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta

import googleapiclient.discovery
import pytz
import requests
from bs4 import BeautifulSoup
from dateutil import parser

from src.helpers import wait_for_internet_if_not_avaible_decorator
from src.logger import LOGGER_NAME
from src.watcher.errors import VideoDoNotExistException

logger = logging.getLogger(LOGGER_NAME)

RESET_UNITS_TIME = time(7, tzinfo=pytz.UTC)
SECOND_IN_DAY = 60 * 60 * 24


@dataclass
class VideoFromApi:
    video_id: str
    url: str
    publish_time: datetime
    title: str


@dataclass
class DetailedVideoFromApi:
    video_id: str
    url: str
    publish_time: datetime
    title: str
    video_lenght: float
    description: str


class YoutubeApi:
    def __init__(self,
                 api_key: str,
                 channel_id: str,
                 channel_name: str,
                 max_checks_per_day=7000
                 ):
        self.API_KEY = api_key
        self.channel_id = channel_id
        self.channel_name = channel_name
        self._reset_unit_datetime: datetime = YoutubeApi._get_next_reset_units_datetime()
        self._max_checks_per_day = max_checks_per_day
        self._used_points: int = 0
        self.ytb = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    @staticmethod
    def _add_points_decorator(points: int):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if datetime.now(tz=pytz.UTC) >= self._reset_unit_datetime:
                    self._used_points = 0
                    self._reset_unit_datetime = YoutubeApi._get_next_reset_units_datetime()
                self._used_points += points
                return func(self, *args, **kwargs)

            return wrapper

        return decorator

    @wait_for_internet_if_not_avaible_decorator()
    @_add_points_decorator(1)
    def get_video_count(self) -> int:
        """
        make request to Youtube api to get number of videos of users
        :return: number of videos on channel
        """
        resp = self.ytb.channels().list(part="statistics", id=self.channel_id).execute()
        video_count = resp['items'][0]['statistics']['videoCount']
        logger.debug(f'video count is {video_count} and used points is {self._used_points}')
        return video_count

    @wait_for_internet_if_not_avaible_decorator()
    @_add_points_decorator(100)
    def get_detailed_video(self, video_id: str) -> DetailedVideoFromApi:
        logger.debug(f'getting detailed video {video_id} and actual used points are {self._used_points}')
        resp = self.ytb.videos().list(part="snippet,contentDetails", id=video_id).execute()
        if len(resp["items"]) < 1:
            raise VideoDoNotExistException(f"VideoFromApi with video_id {video_id} do not exist")
        item = resp['items'][0]
        video = DetailedVideoFromApi(
            video_id=item["id"],
            url=YoutubeApi._get_video_url(video_id=item["id"]),
            publish_time=YoutubeApi._parse_datetime(item["snippet"]["publishedAt"]),
            title=item["snippet"]["title"],
            video_lenght=YoutubeApi._parse_duration(item["contentDetails"]["duration"]),
            description=item["snippet"]["description"]
        )
        return video

    @wait_for_internet_if_not_avaible_decorator()
    @_add_points_decorator(100)
    def get_latest_videos_from_api(self, count=1) -> list[VideoFromApi]:
        logger.debug(f"getting latest videos from api {count} and actual used points are {self._used_points}")
        resp = self.ytb.search().list(key=self.API_KEY, channelId=self.channel_id, part="snippet",
                                      order="date",
                                      maxResults=count).execute()
        videos = []
        for item in resp["items"]:
            if item["id"]["kind"] != "youtube#video":
                continue
            video = VideoFromApi(
                video_id=item["id"]["videoId"],
                url=YoutubeApi._get_video_url(video_id=item["id"]["videoId"]),
                publish_time=YoutubeApi._parse_datetime(item["snippet"]["publishedAt"]),
                title=item["snippet"]["title"]
            )
            videos.append(video)
        return videos

    @property
    def maximum_checks_calls_per_day(self) -> int:
        return self._max_checks_per_day

    @staticmethod
    def _get_video_url(video_id: str):
        return f"https://www.youtube.com/watch?v={video_id}"

    @staticmethod
    def _parse_datetime(date_str: str) -> datetime:
        return parser.parse(date_str)

    @staticmethod
    def _parse_duration(duration: str) -> float:
        '''
        :param duration: time format returned from YouTube api
        :return: class time of duration
        '''
        hours_match = re.search(r'(\d+)H', duration)
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

        return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    @staticmethod
    def _get_next_reset_units_datetime() -> datetime:
        today = datetime.utcnow()
        next_day = today + timedelta(days=1)
        return datetime.combine(next_day.date(), RESET_UNITS_TIME, tzinfo=pytz.UTC)

    # SCRAPING METHOD
    @wait_for_internet_if_not_avaible_decorator()
    def get_latest_videos_from_scrapping(self, count: int) -> list[str]:
        if count > 30:
            raise ValueError("You can get only 30 latest videos")
        resp = requests.get(self._get_channel_url(self.channel_name))
        bs = BeautifulSoup(resp.text, 'html.parser')
        for script in bs.find_all('script'):
            if not script.text.startswith("var ytInitialData = "):
                continue
            data = script.text.removeprefix("var ytInitialData = ").removesuffix(";")
            json_data = json.loads(data)
            x = json_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content'][
                "richGridRenderer"]
            videos_id = []
            for vid in range(count):
                videos_id.append(x['contents'][vid]['richItemRenderer']['content']['videoRenderer']['videoId'])
            return videos_id
        return []

    @staticmethod
    def _get_channel_url(channel_name: str):
        return f"https://www.youtube.com/@{channel_name}/videos"
