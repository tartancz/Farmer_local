from src.database.model import Model


class CodeModel(Model):
    def insert(self,
               video_id: int,
               code: str,
               how_long_to_process_in_total: float,
               code_state_id: int,
               timestamp: float,
               path_to_frame: str
               ):
        SQL = '''
            INSERT INTO code (video_id, code, how_long_to_process_in_total, code_state_id, timestamp, path_to_frame)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self.run_sql_and_commit(SQL, [video_id, code, how_long_to_process_in_total, code_state_id, timestamp, path_to_frame])
