import logging
import queue
from pathlib import Path
import os
from logging.handlers import QueueHandler, TimedRotatingFileHandler, QueueListener
import requests

from src.setting import LOGGING_PATH_FOLDER, DISCORD_CHANNEL, DISCORD_BOT_ID



class DiscordHandler(logging.Handler):
    def __init__(self,
                 channel_id: int,
                 bot_token: str,
                 ):
        self.channel_url = DiscordHandler._getDiscordUrl(channel_id)
        self.bot_token = bot_token
        logging.Handler.__init__(self=self)

    @staticmethod
    def _getDiscordUrl(channel_id: int):
        return f'https://discord.com/api/channels/{channel_id}/messages'

    def emit(self, record: logging.LogRecord):
        requests.post(
            self.channel_url,
            headers={'Authorization': f'Bot {self.bot_token}'},
            json={'content': record.msg},
        )




def configure_loggers():
    logger_queue = queue.Queue(-1)
    queue_handler = QueueHandler(logger_queue)

    root_logger = logging.getLogger("main")
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    #mkdir for logging
    Path(LOGGING_PATH_FOLDER).mkdir(parents=True, exist_ok=True)

    logs_file = os.path.join(LOGGING_PATH_FOLDER, "app.log")

    file_handler = TimedRotatingFileHandler(
        logs_file,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
        delay=False,
    )

    file_handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(filename)s - [%(funcName)s]: %(message)s",
            datefmt="%d/%m/%y %H:%M:%S",
        )
    )

    discord_handler = DiscordHandler(
        DISCORD_CHANNEL,
        DISCORD_BOT_ID
    )
    discord_handler.setLevel(logging.INFO)




    queue_listener = QueueListener(
        logger_queue, file_handler, discord_handler, respect_handler_level=True
    )
    queue_listener.start()

