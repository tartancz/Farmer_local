from src.redeemer.redeemer import Redeemer, CodeState


class RedeemerMock(Redeemer):
    already_redeemed = set()
    valid_codes = ['123456789', '5555']

    def redeem_code(self, code: str) -> CodeState:
        if code in self.already_redeemed:
            return CodeState.ALREADY_TAKEN
        if code in self.valid_codes:
            self.already_redeemed.add(code)
            return CodeState.SUCCESSFULLY_REDEEM
        return CodeState.BAD_CODE
