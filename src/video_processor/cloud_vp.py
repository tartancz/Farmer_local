import queue
import threading
from typing import Generator
import logging

import modal

from src.cloud_types import CodeType
from src.video_processor.video_processor import VideoProcessor
from src.watcher.youtube_api import DetailedVideoFromApi
from src.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)

class ModalVP(VideoProcessor):
    def __init__(self, app_name: str, process_video_name_function: str, youtube_download_name_function: str):
        self.process_video_func = modal.Function.lookup(app_name, process_video_name_function)
        self.youtube_download_func = modal.Function.lookup(app_name, youtube_download_name_function)

    def get_codes(self, video: DetailedVideoFromApi) -> Generator[CodeType, None, None]:
        threading.Thread(target=self.youtube_download_func.remote, args=(video.video_id,)).start()
        q = queue.Queue()

        def worker(part, total_parts):
            for code_type in self.process_video_func.remote_gen(video.video_id, part, total_parts):
                q.put(code_type)

        worker_count = int(video.video_lenght // 180)
        if worker_count == 0:
            worker_count = 1
        if worker_count > 40:
            worker_count = 40
        self.prewarm_processor(worker_count)

        workers = [threading.Thread(target=worker, args=(part, worker_count)) for part in range(worker_count)]
        for worker in workers:
            worker.start()
        while any(t.is_alive() for t in workers) or not q.empty():
            try:
                result = q.get(timeout=10)  # Adjust timeout as needed
                yield result
                q.task_done()
            except queue.Empty:
                continue
        self.downwarm_processor()
        self.delete_video(video)

    def delete_video(self, video: DetailedVideoFromApi):
        vol = modal.Volume.from_name("videos")
        try:
            vol.remove_file(video.video_id + "_complete.mp4")
        except Exception:
            logging.discord("Failed to delete video file, probably youtube_download_func failed to download it.")

    def downwarm_processor(self):
        self.process_video_func.keep_warm(0)
        self.youtube_download_func.keep_warm(0)

    def prewarm_processor(self, count: int = 40):
        self.process_video_func.keep_warm(count)
        self.youtube_download_func.keep_warm(1)
