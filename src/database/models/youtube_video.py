from dataclasses import dataclass
from datetime import datetime

from src.database.model import Model


@dataclass
class YoutubeVideo:
    video_id: str
    channel_id: str
    description: str
    publish_time: datetime
    video_length: float
    url: str
    skipped_finding: bool
    created_at: int


class YoutubeVideoModel(Model):
    def insert(self,
               video_id: str,
               channel_id: str,
               publish_time: datetime,
               title: str,
               url: str,
               skipped_finding: bool,
               description: str | None = None,
               video_length: float | None = None,
               ):
        insert_query = '''
            INSERT INTO youtube_video (video_id, channel_id, description, title, publish_time, video_length, url, skipped_finding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.run_sql_and_commit(insert_query,
                                [video_id, channel_id, description, title, publish_time, video_length, url,
                                 skipped_finding])

    def is_video_in_db(self, video_id: str) -> bool:
        select_query = '''
            SELECT EXISTS(SELECT *
            FROM youtube_video
            WHERE video_id = ?)
        '''
        self.run_sql(select_query, [video_id])
        return self._cursor.fetchone()[0]
