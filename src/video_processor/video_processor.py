from abc import ABC, abstractmethod
from typing import Generator


from src.watcher.youtube_api import DetailedVideoFromApi
from src.cloud_types import CodeType

class VideoProcessor(ABC):

    @abstractmethod
    def get_codes(self, video: DetailedVideoFromApi) -> Generator[CodeType, None, None]:
        pass

    def boot_up_processor(self):
        pass

    def shutdown_processor(self):
        pass