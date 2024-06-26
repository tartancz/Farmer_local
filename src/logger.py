import logging
import os
import queue
from logging.handlers import QueueHandler, TimedRotatingFileHandler, QueueListener
from pathlib import Path

import requests

from src.setting import LOGGING_PATH_FOLDER, DISCORD_CHANNEL, DISCORD_BOT_ID

DISCORD_LEVEL = logging.INFO + 5
LOGGER_NAME = "main"


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
        try:
            requests.post(
                self.channel_url,
                headers={'Authorization': f'Bot {self.bot_token}'},
                json={'content': record.msg},
            )
        except Exception:
            pass


# https://stackoverflow.com/a/35804945
def add_loging_level(level_name: str, level_num: int, method_name: str = None):
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError('{} already defined in logging module'.format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError('{} already defined in logging module'.format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError('{} already defined in logger class'.format(method_name))

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, logForLevel)
    setattr(logging, method_name, logToRoot)


def configure_loggers():
    add_loging_level("DISCORD", DISCORD_LEVEL)

    logger_queue = queue.Queue(-1)
    queue_handler = QueueHandler(logger_queue)

    root_logger = logging.getLogger(LOGGER_NAME)
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    log_format = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(filename)s - [%(funcName)s]: %(message)s",
            datefmt="%d/%m/%y %H:%M:%S",
    )

    error_handler = logging.FileHandler(os.path.join(LOGGING_PATH_FOLDER, "error.log"))
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)

    # mkdir for logging
    log_path = os.path.join(LOGGING_PATH_FOLDER, "logs")
    Path(log_path).mkdir(parents=True, exist_ok=True)

    logs_file = os.path.join(log_path, "app.log")

    file_handler = TimedRotatingFileHandler(
        logs_file,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
        delay=False,
    )

    file_handler.setFormatter(log_format)

    discord_handler = DiscordHandler(
        DISCORD_CHANNEL,
        DISCORD_BOT_ID
    )
    discord_handler.setLevel(DISCORD_LEVEL)

    queue_listener = QueueListener(
        logger_queue, error_handler, file_handler, discord_handler, respect_handler_level=True
    )
    queue_listener.start()
