import sys
import time
import math
import asyncio
import logging
import yfinance as yf
from collections import defaultdict
from datetime import datetime, timedelta

from quotexpy import expiration
from quotexpy import global_value
from quotexpy.api import QuotexAPI
from quotexpy.constants import codes_asset


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    return defaultdict(lambda: nested_dict(n - 1, type))


def truncate(f, n):
    return math.floor(f * 10**n) / 10**n


class Quotex(object):
    __version__ = "1.40.2"

    def __init__(self, email, password):
        self.size = [
            1,
            5,
            10,
            15,
            30,
            60,
            120,
            300,
            600,
            900,
            1800,
            3600,
            7200,
            14400,
            28800,
            43200,
            86400,
            604800,
            2592000,
        ]
        self.email = email
        self.password = password
        self.set_ssid = None
        self.duration = None
        self.suspend = 0.5
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        self.websocket_client = None
        self.websocket_thread = None
        self.debug_ws_enable = False
        self.api = None

        self.logger = logging.getLogger(__name__)

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    @staticmethod
    def check_connect():
        if global_value.check_websocket_if_connect == 0:
            return False
        return True

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
                self.logger.error("**error** api.get_instruments need reconnect")
                await self.connect()
        return self.api.instruments

    def get_all_asset_name(self):
        if self.api.instruments:
            return [instrument[2].replace("\n", "") for instrument in self.api.instruments]

    def check_asset_open(self, instrument):
        if self.api.instruments:
            for i in self.api.instruments:
                if instrument == i[2]:
                    return i[0], i[2], i[14]

    async def get_candles(self, asset, offset, period=None):
        index = expiration.get_timestamp()
        # index - offset
        if period:
            period = expiration.get_period_time(period)
        else:
            period = index
        self.api.current_asset = asset
        self.api.candles.candles_data = None
        while True:
            try:
                self.api.get_candles(codes_asset[asset], offset, period, index)
                while self.check_connect and self.api.candles.candles_data is None:
                    await asyncio.sleep(0.1)
                if self.api.candles.candles_data is not None:
                    break
            except:
                self.logger.error("**error** get_candles need reconnect")
                await self.connect()
        return self.api.candles.candles_data

    async def get_candle_v2(self, asset, period):
        self.api.candle_v2_data[asset] = None
        size = 10
        self.stop_candles_stream(asset)
        self.api.subscribe_realtime_candle(asset, size, period)
        while self.api.candle_v2_data[asset] is None:
            await asyncio.sleep(1)
        return self.api.candle_v2_data[asset]

    async def connect(self):
        if global_value.check_websocket_if_connect:
            self.close()
        self.api = QuotexAPI(
            "qxbroker.com",
            self.email,
            self.password,
        )
        self.api.trace_ws = self.debug_ws_enable
        check, reason = await self.api.connect()
        if check:
            self.api.send_ssid(max_attemps=10)
            if global_value.check_accepted_connection == 0:
                check, reason = await self.connect()
                if not check:
                    check, reason = (
                        False,
                        "Access denied, session does not exist!!!",
                    )
        return check, reason

    def change_account(self, mode="PRACTICE"):
        """Change active account `real` or `practice`"""
        if mode.upper() == "REAL":
            self.api.account_type = 0
        elif mode.upper() == "PRACTICE":
            self.api.account_type = 1
        else:
            self.logger.error(f"{mode} does not exist")
            sys.exit(1)
        self.api.send_ssid()

    async def edit_practice_balance(self, amount=None):
        self.api.training_balance_edit_request = None
        self.api.edit_training_balance(amount)
        while self.api.training_balance_edit_request is None:
            await asyncio.sleep(0.1)
        return self.api.training_balance_edit_request

    async def get_balance(self):
        while not self.api.account_balance:
            await asyncio.sleep(0.1)
        balance = (
            self.api.account_balance.get("demoBalance")
            if self.api.account_type > 0
            else self.api.account_balance.get("liveBalance")
        )
        return float(f"{truncate(balance + self.get_profit(), 2):.2f}")

    async def trade(self, action: str, amount, asset: str, duration):
        """Trade Binary option"""
        status_trade = False
        self.duration = duration - 1
        request_id = expiration.get_timestamp()
        self.api.current_asset = asset
        self.api.trade(action, amount, asset, duration, request_id)
        start_time = time.time()
        previous_second = -1
        while not self.api.trade_id:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time
            current_second = int(elapsed_time)
            if current_second != previous_second:
                print(f"\rWaiting for trade operation... Elapsed time: {round(elapsed_time)} seconds", end="")
                previous_second = current_second
            if elapsed_time >= 3:
                break
        else:
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

    async def start_remaing_time(self):
        try:
            now_stamp = datetime.fromtimestamp(expiration.get_timestamp())
            # print("now_stamp",now_stamp)
            expiration_stamp = datetime.fromtimestamp(self.api.timesync.server_timestamp)
            # print("self.api.timesync.server_timestamp",self.api.timesync.server_timestamp)
            # print("self.api.timesync.server_timestamp",expiration_stamp.strftime("%d/%m/%Y %H:%M:%S"))
            # print("expiration_stamp",expiration_stamp)
            remaing_time = int((expiration_stamp - now_stamp).total_seconds())
            # print("remaing_time",remaing_time)
            if remaing_time < 0:
                now_stamp_ajusted = now_stamp - timedelta(seconds=self.duration)
                # print("now_stamp_ajusted",now_stamp_ajusted)
                remaing_time = int((expiration_stamp - now_stamp_ajusted).total_seconds()) + abs(remaing_time)
                # print("remaing_time ajusted",remaing_time)
            while remaing_time >= 0:
                remaing_time -= 1
                print(f"\rWaiting for completion in {remaing_time if remaing_time > 0 else 0} seconds.", end="")
                await asyncio.sleep(1)
        except Exception as e:
            print(e)

    async def check_win(self, asset, id_number):
        """Check win based id"""
        self.logger.debug(f"begin check wind {id_number}")
        await self.start_remaing_time()
        # start_time = time.time()
        # listinfodata_dict = {}
        while True:  # time.time() - start_time < 5:
            try:
                listinfodata_dict = self.api.listinfodata.get(asset)
                if listinfodata_dict and listinfodata_dict["game_state"] == 1:
                    break
                listinfodata_dict = self.api.listinfodata.get(id_number)
                if listinfodata_dict and listinfodata_dict["game_state"] == 1:
                    break
            except:
                pass
            time.sleep(0.1)
        self.logger.debug("end check wind")
        self.api.listinfodata.delete(id_number)
        self.api.listinfodata.delete(asset)
        # if len(listinfodata_dict) == 0:
        #    return None
        return listinfodata_dict["win"]

    def start_candles_stream(self, asset, size, period=0):
        self.api.subscribe_realtime_candle(asset, size, period)

    def stop_candles_stream(self, asset):
        self.api.unsubscribe_realtime_candle(asset)

    def get_realtime_candles(self, asset):
        while True:
            if asset in self.api.realtime_price:
                if len(self.api.realtime_price[asset]) > 0:
                    return self.api.realtime_price[asset]

    def get_signal_data(self):
        return self.api.signal_data

    def get_profit(self):
        return self.api.profit_in_operation or 0

    async def start_candles_one_stream(self, asset, size):
        if str(asset + "," + str(size)) not in self.subscribe_candle:
            self.subscribe_candle.append((asset + "," + str(size)))
        start = time.time()
        self.api.candle_generated_check[str(asset)][int(size)] = {}
        while True:
            if time.time() - start > 20:
                self.logger.error("**error** start_candles_one_stream late for 20 sec")
                return False
            try:
                if self.api.candle_generated_check[str(asset)][int(size)]:
                    return True
            except:
                pass
            try:
                self.api.subscribe(codes_asset[asset], size)
            except:
                self.logger.error("**error** start_candles_stream reconnect")
                await self.connect()
            await asyncio.sleep(1)

    async def start_candles_all_size_stream(self, asset):
        self.api.candle_generated_all_size_check[str(asset)] = {}
        if str(asset) not in self.subscribe_candle_all_size:
            self.subscribe_candle_all_size.append(str(asset))
        start = time.time()
        while True:
            if time.time() - start > 20:
                self.logger.error(f"**error** fail {asset} start_candles_all_size_stream late for 10 sec")
                return False
            try:
                if self.api.candle_generated_all_size_check[str(asset)]:
                    return True
            except:
                pass
            try:
                self.api.subscribe_all_size(codes_asset[asset])
            except:
                self.logger.error("**error** start_candles_all_size_stream reconnect")
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
        self.api.close()

    async def get_moving_average(self, symbol, interval, periods):
        # Obter os dados do par de negociação no intervalo desejado
        data = yf.download(symbol, interval=interval, period="1d")

        # Calcular a média móvel com o número de períodos especificado
        data["Close_MA"] = data["Close"].rolling(window=periods).mean()

        return data["Close_MA"]

    async def get_last_candles(self, symbol, interval):
        ticker = yf.Ticker(symbol)
        last_candles = ticker.history(period="1d", interval=interval)
        return last_candles
