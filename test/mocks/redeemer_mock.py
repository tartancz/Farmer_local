from src.redeemer import CodeState
from src.redeemer.redeemer import Redeemer, CodeState


class RedeemerMock(Redeemer):
    valid_codes = ['123456789', '5555']
    def redeem_code(self, code: str) -> CodeState:
        if code in self.valid_codes:
            return CodeState.SUCCESSFULLY_REDEEM
        return CodeState.BAD_CODE
    