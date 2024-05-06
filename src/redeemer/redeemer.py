from abc import ABC, abstractmethod
from enum import Enum, auto


class CodeState(Enum):
    SUCCESSFULLY_REDEEM = auto()
    ALREADY_TAKEN = auto()
    BAD_CODE = auto()
    EXPIRED = auto()
    TOO_MANY_REQUESTS = auto()
    UNKNOWN_ERROR = auto()


class Redeemer(ABC):
    @abstractmethod
    def redeem_code(self, code: str) -> CodeState:
        pass
