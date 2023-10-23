import json
from quotexpy.utils import unix_time
from quotexpy.ws.channels.base import Base


class Buy(Base):
    """Class for Quotex buy websocket channel"""

    name = "buy"

    def __call__(self, action: str, amount, asset: str, duration, request_id):
        payload = {
            "action": action,
            "amount": amount,
            "asset": asset.replace("_otc", "").strip().upper() if "_otc" in asset else asset.upper(),
            "time": unix_time() + duration,
            "isDemo": self.api.account_type,
            "optionType": 100 if self.api.account_type else 1,
            "requestId": request_id,
            "tournamentId": 0,
        }

        data = f'42["orders/open",{json.dumps(payload)}]'
        self.send_websocket_request(data)
