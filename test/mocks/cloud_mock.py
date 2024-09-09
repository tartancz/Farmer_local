from typing import Generator

from src.cloud_types import CodeType
from src.video_processor.video_processor import VideoProcessor
from src.watcher.youtube_api import DetailedVideoFromApi


class MockProcessor(VideoProcessor):
    def get_codes(self, video: DetailedVideoFromApi) -> Generator[CodeType, None, None]:
        yield {"code": "5555", "timestamp": 2.0, "frame": b"1"}
        yield {"code": "6666", "timestamp": 2.0, "frame": b"1"}
        yield {"code": "123456789", "timestamp": 2.0, "frame": b"1"}