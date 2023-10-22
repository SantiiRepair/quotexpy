import json
from quotexpy.ws.channels.base import Base


class Buy(Base):
    """Class for Quotex buy websocket channel"""

    name = "buy"

    def __call__(self, price, asset, direction, duration, request_id):
        # option_type = 100
        # option_type = 1
        # if "_otc" not in asset:
        #     option_type = 1
        # duration = get_expiration_time(
        #     int(self.api.timesync.server_timestamp), duration)
        # payload = {
        #     "chartId": "graph",
        #     "settings": {
        #         "chartId": "graph",
        #         "chartType": 2,
        #         "currentExpirationTime": duration,
        #         "isFastOption": False,
        #         "isFastAmountOption": False,
        #         "isIndicatorsMinimized": False,
        #         "isIndicatorsShowing": True,
        #         "isShortBetElement": False,
        #         "chartPeriod": 4,
        #         "currentAsset": {
        #             "symbol": asset
        #         },
        #         "dealValue": 5,
        #         "dealPercentValue": 1,
        #         "isVisible": True,
        #         "timePeriod": 30,
        #         "gridOpacity": 8,
        #         "isAutoScrolling": 1,
        #         "isOneClickTrade": True,
        #         "upColor": "#0FAF59",
        #         "downColor": "#FF6251"
        #     }
        # }
        # data = f'42["settings/store",{json.dumps(payload)}]'
        # self.send_websocket_request(data)

        payload = {
            "asset": asset,
            "amount": price,
            "time": duration,
            "action": direction,
            "isDemo": self.api.account_type,
            "tournamentId": 0,
            "requestId": request_id,
            "optionType": 100 if self.api.account_type else 1,
        }

        data = f'42["orders/open",{json.dumps(payload)}]'
        self.send_websocket_request(data)
