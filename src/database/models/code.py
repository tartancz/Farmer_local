from dataclasses import dataclass
from datetime import datetime

from src.database.model import Model


@dataclass
class Code:
    id: int
    video_id: int
    code: str
    how_long_to_process_in_total: float
    code_state_id: int
    activated_by: int
    value: int = None
    created: datetime = None
    timestamp: float = None
    path_to_frame: str = None



class CodeModel(Model):
    def insert(self,
               video_id: int,
               code: str,
               how_long_to_process_in_total: float,
               code_state_id: int,
               activated_by: int,
               value: int | None = None,
               timestamp: float | None = None,
               path_to_frame: str | None = None,
               ):
        SQL = f'''
            INSERT INTO {self.table_name} (video_id, code, how_long_to_process_in_total, code_state_id, activated_by, value, timestamp, path_to_frame)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.run_sql_and_commit(SQL,
                                [video_id, code, how_long_to_process_in_total, code_state_id, activated_by, value, timestamp, path_to_frame])

    def get_codes_by_video_id(self, video_id: int) -> list[Code]:
        sql = f'''
            SELECT id, video_id, code, how_long_to_process_in_total, code_state_id, activated_by, value, created, timestamp, path_to_frame
            FROM {self.table_name} 
            where video_id = ?
        '''
        data = self.run_and_fechall(sql, (video_id,))
        result = []
        for row in data:
            result.append(Code(
                id=row[0],
                video_id=row[1],
                code=row[2],
                how_long_to_process_in_total=row[3],
                code_state_id=row[4],
                activated_by=row[5],
                value=row[6],
                created=row[7],
                timestamp=row[8],
                path_to_frame=row[9],
            ))
        return result
