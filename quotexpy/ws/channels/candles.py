import json
from quotexpy.ws.channels.base import Base


class GetCandles(Base):
    """Class for Quotex candles websocket channel."""

    name = "candles"

    def __call__(self, asset, index, offset, period, time):
        """Method to send message to candles websocket channel."""
        payload = {"asset": asset, "index": index, "offset": offset, "period": period, "time": time}
        data = f'42["history/load",{json.dumps(payload)}]'
        self.send_websocket_request(data)
