import logging
from time import sleep

import requests

from src.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def wait_for_internet_if_not_avaible_decorator():
    # TODO: add options maximum retries
    def decorator(func):
        def wrapper(*args, **kwargs):
            while True:
                isInternetAvaible = True
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    while True:
                        try:
                            requests.get("https://www.google.com")
                        except Exception:
                            logger.debug("No internet connection")
                            isInternetAvaible = False
                            sleep(1)
                            continue
                        if isInternetAvaible:
                            raise e
                        else:
                            logger.info("Internet connection established")
                            break

        return wrapper

    return decorator


def wolt_get_value_from_code(code: str) -> int:
    '''
    This function will return value from code.
    if code cant be converted to int it will return 0
    '''
    try:
        return int(code[2:5])
    except ValueError:
        return 0