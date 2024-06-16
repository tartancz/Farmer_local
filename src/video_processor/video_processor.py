from abc import ABC, abstractmethod
from typing import Generator

from src.cloud_types import CodeType
from src.watcher.youtube_api import DetailedVideoFromApi


class VideoProcessor(ABC):

    @abstractmethod
    def get_codes(self, video: DetailedVideoFromApi) -> Generator[CodeType, None, None]:
        pass

    def delete_video(self, video: DetailedVideoFromApi):
        pass

    def prewarm_processor(self, count: int = 40):
        pass

    def downwarm_processor(self):
        pass
