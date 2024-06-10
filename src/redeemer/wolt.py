import logging
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import TYPE_CHECKING

import requests

from src.database import Database, RowDontExistException
from src.logger import LOGGER_NAME
from src.redeemer.errors import RefreshAuthFailedException, NotAuthorizedException
from src.redeemer.redeemer import Redeemer, CodeState

if TYPE_CHECKING:
    from requests import Response

ACCESS_TOKEN_URL = 'https://authentication.wolt.com/v1/wauth2/access_token'
REDEEM_DISCOUNT_URL = 'https://restaurant-api.wolt.com/v2/credit_codes/consume'

logger = logging.getLogger(LOGGER_NAME)


@dataclass
class WoltTokenFromResponse:
    refresh_token: str
    access_token: str
    expires_in: int
    created: datetime = None

    def __post_init__(self):
        self.created = datetime.utcnow()


class Wolt(Redeemer):
    def __init__(self, db: Database, account_name: str):
        self._db = db
        # will check if account exist in database
        try:
            self.account = self._db.wolt_account.get_by_account_name(account_name)
        except RowDontExistException:
            print("account was not found in database, please run create_wolt_account.py script to create new account.")
            exit(1)
        # get latest token for account
        logger.info(f"got Wolt account name: {self.account.account_name}")
        token = self._db.wolt_token.get_latest_token(self.account.id)
        self.actual_token = Wolt.make_request_to_new_token(token.refresh_token)
        self._db.wolt_token.insert(
            account_id=self.account.id,
            refresh_token=self.actual_token.refresh_token,
            access_token=self.actual_token.access_token,
        )

    @staticmethod
    def create_new_account(db: Database, account_name: str, refresh_token: str):

        with db.transaction:
            account_id = db.wolt_account.insert(account_name)
            token = Wolt.make_request_to_new_token(refresh_token)
            db.wolt_token.insert(
                account_id,
                token.refresh_token,
                token.access_token,
                token.expires_in
            )

    @staticmethod
    def make_request_to_new_token(refresh_token: str) -> WoltTokenFromResponse:
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        response = requests.post(ACCESS_TOKEN_URL, data=data)
        if response.status_code != 200:
            raise RefreshAuthFailedException(
                f"auth failed with status code: {response.status_code} and text: {response.text}")
        response_json = response.json()
        wolt_token = WoltTokenFromResponse(
            refresh_token=response_json['refresh_token'],
            access_token=response_json['access_token'],
            expires_in=response_json['expires_in']
        )
        return wolt_token

    def get_new_token(self):
        self.actual_token = Wolt.make_request_to_new_token(self.actual_token.refresh_token)
        self._db.wolt_token.insert(
            self.account.id,
            self.actual_token.refresh_token,
            self.actual_token.access_token,
            self.actual_token.expires_in
        )

    def redeem_code(self, code: str) -> CodeState:
        if self.is_token_expired():
            logger.debug("token is expired, getting new...")
            self.get_new_token()

        response = self._make_request_to_code_redeem(code)
        if response.status_code == 401:
            raise NotAuthorizedException("Wolt is not authorized, use get_new_token function.")
        elif response.status_code == 404:
            return CodeState.BAD_CODE
        elif response.status_code == 403:
            resp = response.json()
            if resp.get("error_code") == 482:
                return CodeState.ALREADY_TAKEN
            return CodeState.EXPIRED
        elif response.status_code == 429:
            return CodeState.TOO_MANY_REQUESTS
        elif response.status_code == 201:
            return CodeState.SUCCESSFULLY_REDEEM
        return CodeState.UNKNOWN_ERROR  # type: ignore

    def _make_request_to_code_redeem(self, code: str) -> 'Response':
        logger.info(f"redeming code {code}")
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f'Bearer {self.actual_token.access_token}',
        }
        data = {
            "code": code
        }
        return requests.post(REDEEM_DISCOUNT_URL, headers=headers, json=data)

    def is_token_expired(self) -> bool:
        return self.actual_token.created + timedelta(
            seconds=self.actual_token.expires_in - 10) <= datetime.utcnow()  # - 10 is buffer for delay
