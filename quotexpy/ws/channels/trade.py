import json
from quotexpy.ws.channels.base import Base


class Trade(Base):
    """Class for Quotex trade websocket channel"""

    def __call__(self, action: str, amount, asset: str, duration: int, request_id: int):
        payload = {
            "asset": asset,
            "amount": amount,
            "time": duration,
            "action": action,
            "isDemo": self.api.account_type,
            "tournamentId": 0,
            "requestId": request_id,
            "optionType": 100 if self.api.account_type else 1,
        }

        data = f'42["orders/open",{json.dumps(payload)}]'
        self.send_websocket_request(data)
