"""A python wrapper for Quotex API"""

import time
import typing
import asyncio
import logging
from datetime import datetime, timedelta

from quotexpy import expiration
from quotexpy.api import QuotexAPI
from quotexpy.utils import log_file_path
from quotexpy.constants import codes_asset
from quotexpy.utils.account_type import AccountType


class Quotex(object):
    def __init__(self, email="", password="", **kwargs):
        self.api = None
        self.email = email
        self.password = password
        self.kwargs = kwargs

        self.suspend = 0.5
        self.duration = None

        self.subscribe_mood = []
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []

        self.trace_ws = False
        self.websocket_client = None
        self.websocket_thread = None

        self.logger = logging.getLogger(__name__)

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    async def connect(self) -> bool:
        self.api = QuotexAPI(self.email, self.password, **self.kwargs)
        self.api.trace_ws = self.trace_ws
        ok = await self.api.connect()
        if ok:
            self.api.send_ssid(max_attemps=10)
            if self.api.check_accepted_connection == 0:
                ok = await self.connect()

        return ok

    def check_connect(self):
        if isinstance(self.api, QuotexAPI) and self.api.check_websocket_if_connect == 1:
            return True
        return False

    async def re_subscribe_stream(self):
        try:
            for ac in self.subscribe_candle:
                sp = ac.split(",")
                await self.start_candles_one_stream(sp[0], sp[1])
        except:
            pass
        try:
            for ac in self.subscribe_candle_all_size:
                await self.start_candles_all_size_stream(ac)
        except:
            pass
        try:
            for ac in self.subscribe_mood:
                await self.start_mood_stream(ac)
        except:
            pass

    async def get_instruments(self):
        await asyncio.sleep(self.suspend)
        self.api.instruments = None
        while self.api.instruments is None:
            try:
                await self.api.get_instruments()
                start = time.time()
                while self.api.instruments is None and time.time() - start < 10:
                    await asyncio.sleep(0.1)
            except:
                await self.connect()
        return self.api.instruments

    def get_all_asset_name(self):
        if self.api.instruments:
            return [instrument[2].replace("\n", "") for instrument in self.api.instruments]

    def check_asset(self, asset: str) -> typing.Union[typing.Tuple[int, str, bool], None]:
        if isinstance(self.api, QuotexAPI) and self.api.instruments:
            for i in self.api.instruments:
                if asset == i[2]:
                    return i[0], i[2], i[14]

        return None

    async def get_candles(self, asset: str, offset: int, period: int) -> typing.List[typing.Union[typing.List, None]]:
        self.api.current_asset = asset
        index = expiration.get_timestamp()
        self.api.candles.candles_data = None
        while True:
            try:
                tm = expiration.get_timestamp()
                self.api.get_candles(asset, index, offset, period, tm)
                while self.check_connect and self.api.candles.candles_data is None:
                    await asyncio.sleep(0.1)
                if self.api.candles.candles_data is not None:
                    break
            except:
                await self.connect()

        return self.api.candles.candles_data

    async def get_candle_v2(self, asset: str, period: int) -> typing.List[typing.Union[typing.Dict, None]]:
        self.api.candle_v2_data[asset] = None
        self.stop_candles_stream(asset)
        self.api.subscribe_realtime_candle(asset, period)
        while self.api.candle_v2_data[asset] is None:
            await asyncio.sleep(1)

        return self.api.candle_v2_data[asset]

    def change_account(self, mode=AccountType.PRACTICE) -> None:
        """Change active account `real` or `practice`"""
        if mode.upper() == AccountType.REAL:
            self.api.account_type = 0
        elif mode.upper() == AccountType.PRACTICE:
            self.api.account_type = 1
        else:
            raise ValueError(f"{mode} does not exist")
        self.api.send_ssid()

    @property
    def account_type(self):
        return AccountType.PRACTICE if self.api.account_type == 1 else AccountType.REAL

    async def edit_practice_balance(self, amount=None):
        self.api.training_balance_edit_request = None
        self.api.edit_training_balance(amount)
        while self.api.training_balance_edit_request is None:
            await asyncio.sleep(0.1)
        return self.api.training_balance_edit_request

    async def get_balance(self) -> float:
        while not self.api.account_balance:
            await asyncio.sleep(0.1)

        balance = (
            self.api.account_balance.get("demoBalance")
            if self.api.account_type > 0
            else self.api.account_balance.get("liveBalance")
        )

        return balance

    async def trade(
        self, action: str, amount, asset: str, duration
    ) -> typing.Tuple[bool, typing.Union[typing.Dict, None]]:
        """Trade Binary option"""
        status_trade = False
        self.api.trade_id = None
        self.duration = duration
        self.api.current_asset = asset
        request_id = expiration.get_timestamp()
        self.api.subscribe_realtime_candle(asset, duration)
        self.api.trade(action, amount, asset, duration, request_id)
        while self.api.trade_id is None:
            await asyncio.sleep(0.1)
            if self.api.check_websocket_if_error:
                return False, self.api.websocket_error_reason

        status_trade = True
        return status_trade, self.api.trade_successful

    async def sell_option(self, options_ids):
        """Sell asset Quotex"""
        self.api.sell_option(options_ids)
        self.api.sold_options_respond = None
        while self.api.sold_options_respond is None:
            await asyncio.sleep(0.1)
        return self.api.sold_options_respond

    def get_payment(self):
        """Payment Quotex server"""
        assets_data = {}
        for i in self.api.instruments:
            assets_data[i[2]] = {"turbo_payment": i[18], "payment": i[5], "open": i[14]}
        return assets_data

    async def __start_remaining_time(self):
        try:
            now_stamp = datetime.fromtimestamp(expiration.get_timestamp())
            expiration_stamp = datetime.fromtimestamp(self.api.timesync.server_timestamp)
            remaining_time = int((expiration_stamp - now_stamp).total_seconds())
            if remaining_time < 0:
                now_stamp_ajusted = now_stamp - timedelta(seconds=self.duration)
                remaining_time = int((expiration_stamp - now_stamp_ajusted).total_seconds()) + abs(remaining_time)
            while remaining_time >= 0:
                remaining_time -= 1
                await asyncio.sleep(1)
        except Exception as err:
            self.logger.error(err)

        self.duration = None
        return True

    async def check_win(self, id_number: str, revisions=5) -> bool:
        """Check win based id"""
        crevisions = 0
        self.logger.debug(f"begin check win {id_number}")
        await self.__start_remaining_time()
        while crevisions < revisions or not self.api.last_operation:
            try:
                crevisions += 1
                await asyncio.sleep(0.1)
                if self.api.last_operation.get("id") == id_number:
                    params = {}
                    self.api.profit_in_operation = self.api.last_operation.get("profit")
                    params["win"] = True if self.api.last_operation.get("profit") > 0 else False
                    params["game_state"] = 1
                    self.api.listinfodata.set(id_number, params["win"], params["game_state"])

                result = self.api.listinfodata.get(id_number)
                if isinstance(result, dict) and "win" in result:
                    self.logger.debug("end check win")
                    self.api.listinfodata.delete(id_number)
                    return result["win"]

                if crevisions == revisions:
                    return False
            except Exception as err:
                raise err

    def start_candles_stream(self, asset, period=0):
        self.api.subscribe_realtime_candle(asset, period)

    def stop_candles_stream(self, asset):
        self.api.unsubscribe_realtime_candle(asset)

    def get_realtime_candles(self, asset):
        while True:
            if asset in self.api.realtime_price:
                if len(self.api.realtime_price[asset]) > 0:
                    return self.api.realtime_price[asset]

    def get_signal_data(self):
        return self.api.signal_data

    def get_profit(self) -> float:
        return self.api.profit_in_operation or 0

    async def start_candles_one_stream(self, asset, size):
        if str(asset + "," + str(size)) not in self.subscribe_candle:
            self.subscribe_candle.append((asset + "," + str(size)))
        start = time.time()
        self.api.candle_generated_check[str(asset)][int(size)] = {}
        while True:
            if time.time() - start > 20:
                self.logger.error("start_candles_one_stream late for 20 sec")
                return False
            try:
                if self.api.candle_generated_check[str(asset)][int(size)]:
                    return True
            except:
                pass
            try:
                self.api.subscribe(codes_asset[asset], size)
            except:
                self.logger.error("start_candles_stream reconnect")
                await self.connect()
            await asyncio.sleep(1)

    async def start_candles_all_size_stream(self, asset):
        self.api.candle_generated_all_size_check[str(asset)] = {}
        if str(asset) not in self.subscribe_candle_all_size:
            self.subscribe_candle_all_size.append(str(asset))
        start = time.time()
        while True:
            if time.time() - start > 20:
                self.logger.error(f"fail {asset} start_candles_all_size_stream late for 10 sec")
                return False
            try:
                if self.api.candle_generated_all_size_check[str(asset)]:
                    return True
            except:
                pass
            try:
                self.api.subscribe_all_size(codes_asset[asset])
            except:
                self.logger.error("start_candles_all_size_stream reconnect")
                await self.connect()
            await asyncio.sleep(1)

    async def start_mood_stream(self, asset, instrument="turbo-option"):
        if asset not in self.subscribe_mood:
            self.subscribe_mood.append(asset)
        while True:
            self.api.subscribe_Traders_mood(asset[asset], instrument)
            try:
                self.api.traders_mood[codes_asset[asset]] = codes_asset[asset]
                break
            except:
                await asyncio.sleep(5)

    def close(self):
        if isinstance(self.api, QuotexAPI):
            self.api.close()


logging.basicConfig(
    filename=log_file_path,
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
