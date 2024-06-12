from typing import Generator

import modal

from src.cloud_types import CodeType
from src.video_processor.video_processor import VideoProcessor
from src.watcher.youtube_api import DetailedVideoFromApi


class ModalVP(VideoProcessor):
    def __init__(self,
                 app_name: str,
                 process_video_name_function: str,
                 ):
        self.download_video_func = modal.Function.lookup(app_name, process_video_name_function)

    def get_codes(self, video: DetailedVideoFromApi) -> Generator[CodeType, None]:
        yield from self.download_video_func.remote_gen(video.video_id)

    def shutdown_processor(self):
        self.download_video_func.keep_warm(0)

    def boot_up_processor(self):
        self.download_video_func.keep_warm(1)
