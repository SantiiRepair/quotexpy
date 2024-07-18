"""Module for Quotex websocket"""

import os
import ssl
import time
import json
import pickle
import typing
import certifi
import logging
import urllib3
import threading

from quotexpy.exceptions import QuotexTimeout
from quotexpy.http.login import Login
from quotexpy.http.logout import Logout
from quotexpy.ws.channels.ssid import Ssid
from quotexpy.ws.channels.trade import Trade
from quotexpy.ws.channels.candles import GetCandles
from quotexpy.ws.channels.sell_option import SellOption
from quotexpy.ws.objects.timesync import TimeSync
from quotexpy.ws.objects.candles import Candles
from quotexpy.ws.objects.profile import Profile
from quotexpy.ws.objects.listinfodata import ListInfoData
from quotexpy.ws.client import WebsocketClient
from collections import defaultdict

urllib3.disable_warnings()
logger = logging.getLogger(__name__)

cert_path = certifi.where()
os.environ["SSL_CERT_FILE"] = cert_path
os.environ["WEBSOCKET_CLIENT_CA_BUNDLE"] = cert_path
cacert = os.environ.get("WEBSOCKET_CLIENT_CA_BUNDLE")


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    return defaultdict(lambda: nested_dict(n - 1, type))


class QuotexAPI(object):
    """Class for communication with Quotex API"""

    socket_option_opened = {}
    trade_id = None
    trace_ws = False
    buy_expiration = None
    current_asset = None
    trade_successful = None
    account_balance = None
    last_operation = {}
    account_type = None
    instruments = None
    training_balance_edit_request = None
    profit_in_operation = None
    sold_options_respond = None
    sold_digital_options_respond = None
    listinfodata = ListInfoData()
    timesync = TimeSync()
    candles = Candles()

    SSID = None
    wss_message = None
    check_websocket_if_connect = None
    ssl_Mutual_exclusion = False
    ssl_Mutual_exclusion_write = False
    started_listen_instruments = True
    check_rejected_connection = False
    check_accepted_connection = False
    check_websocket_if_error = False
    websocket_error_reason = None
    balance_id = None

    def __init__(self, email: str, password: str, **kwargs):
        """
        :param str email: The email of a Quotex server.
        :param str password: The password of a Quotex server.
        """
        self.email = email
        self.password = password
        self.kwargs = kwargs
        self._temp_status = ""
        self.settings_list = {}
        self.signal_data = nested_dict(2, dict)
        self.get_candle_data = {}
        self.candle_v2_data = {}
        self.cookies = None
        self.profile = None
        self.websocket_thread = None
        self.wss_url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
        self.websocket_client = None
        self.set_ssid = None
        self.user_agent = None
        self.token_login2fa = None
        self.realtime_price = {}
        self.realtime_sentiment = {}
        self.profile = Profile()

        self.logger = logging.getLogger(__name__)

    @property
    def websocket(self):
        """Property to get websocket.

        :returns: The instance of :class:`WebSocket <websocket.WebSocket>`.
        """
        return self.websocket_client.wss

    def get_candle_v2(self):
        payload = {"_placeholder": True, "num": 0}
        data = f'451-["history/list/v2", {json.dumps(payload)}]'
        return self.send_websocket_request(data)

    def subscribe_realtime_candle(self, asset: str, period: int):
        self.realtime_price[asset] = []
        payload = {"asset": asset, "period": period}
        data = f'42["instruments/update", {json.dumps(payload)}]'
        self.send_websocket_request(data)
        payload = {"asset": asset, "period": period}
        data = f'42["depth/follow", "{asset}"]'
        self.send_websocket_request(data)
        payload = {"asset": asset, "version": "1.0.0"}
        data = f'42["chart_notification/get", {json.dumps(payload)}]'
        self.send_websocket_request(data)
        return self.send_websocket_request('42["tick"]')

    def unsubscribe_realtime_candle(self, asset):
        data = f'42["subfor", {json.dumps(asset)}]'
        return self.send_websocket_request(data)

    @property
    def logout(self):
        """Property for get Quotex http login resource.
        :returns: The instance of :class:`Login
            <quotexpy.http.login.Login>`.
        """
        return Logout(self)

    @property
    def login(self):
        """Property for get Quotex http login resource.
        :returns: The instance of :class:`Login
            <quotexpy.http.login.Login>`.
        """
        return Login(self)

    @property
    def ssid(self):
        """Property for get Quotex websocket ssid channel.
        :returns: The instance of :class:`Ssid
            <quotexpy.ws.channels.ssid.Ssid>`.
        """
        return Ssid(self)

    @property
    def trade(self):
        """Property for get Quotex websocket ssid channel.
        :returns: The instance of :class:`Buy
            <Quotex.ws.channels.buy.Buy>`.
        """
        return Trade(self)

    @property
    def sell_option(self):
        return SellOption(self)

    @property
    def get_candles(self):
        """Property for get Quotex websocket candles channel.

        :returns: The instance of :class:`GetCandles
            <quotexpy.ws.channels.candles.GetCandles>`.
        """
        return GetCandles(self)

    def check_session(self) -> typing.Tuple[str, str]:
        data = {}
        if os.path.isfile(".session.pkl"):
            with open(".session.pkl", "rb") as file:
                data = pickle.load(file)

            sessions = data.get(self.email, [])
            for session in sessions:
                return session.get("ssid", ""), session.get("cookies", "")
        return "", ""

    def send_websocket_request(self, data, no_force_send=True) -> None:
        """Send websocket request to Quotex server.
        :param str data: The websocket request data.
        :param bool no_force_send: Default None.
        """
        if self.check_websocket_if_connect == 0:
            self.logger.info("websocket connection closed")
            return

        while (self.ssl_Mutual_exclusion or self.ssl_Mutual_exclusion_write) and no_force_send:
            pass

        self.ssl_Mutual_exclusion_write = True
        self.websocket.send('42["tick"]')
        self.websocket.send('42["indicator/list"]')
        self.websocket.send('42["drawing/load"]')
        self.websocket.send('42["pending/list"]')
        self.websocket.send('42["instruments/update",{"asset":"%s","period":60}]' % self.current_asset)
        self.websocket.send('42["chart_notification/get"]')
        self.websocket.send('42["depth/follow","%s"]' % self.current_asset)
        self.websocket.send(data)
        self.logger.debug(data)
        self.ssl_Mutual_exclusion_write = False

    def edit_training_balance(self, amount) -> None:
        data = f'42["demo/refill",{json.dumps(amount)}]'
        self.send_websocket_request(data)

    async def get_ssid(self) -> typing.Tuple[str, str]:
        self.logger.info("authenticating user")
        ssid, cookies = self.check_session()
        if not ssid:
            ssid, cookies = await self.login(self.email, self.password, **self.kwargs)
            self.logger.info("login successful")
        return ssid, cookies

    def start_websocket(self) -> bool:
        self.check_websocket_if_connect = None
        self.check_websocket_if_error = False
        self.websocket_error_reason = None
        self.websocket_client = WebsocketClient(self)
        self.websocket_thread = threading.Thread(
            target=self.websocket.run_forever,
            kwargs={
                "ping_interval": 25000,
                "ping_timeout": 5000,
                "ping_payload": "2",
                "origin": "https://qxbroker.com",
                "host": "ws2.qxbroker.com",
                "sslopt": {
                    "cert_reqs": ssl.CERT_NONE,
                    "ca_certs": cacert,
                    "ssl_version": ssl.PROTOCOL_TLSv1_2,
                },
            },
        )

        self.websocket_thread.daemon = True
        self.websocket_thread.start()

        while True:
            try:
                if self.check_websocket_if_error:
                    self.logger.error(self.websocket_error_reason)
                    return False
                if self.check_websocket_if_connect == 0:
                    self.logger.debug("websocket connection closed")
                    return False
                if self.check_websocket_if_connect == 1:
                    self.logger.debug("websocket successfully connected")
                    return True
            except:
                pass

    def send_ssid(self, max_attemps=10) -> bool:
        """
        Send ssid to Quotex
            max_attemps - time to wait for authorization in seconds
        """
        self.profile.msg = None
        if not self.SSID:
            if os.path.exists(os.path.join(".session.pkl")):
                os.remove(".session.pkl")
            return False

        self.ssid(self.SSID)
        start_time = time.time()
        previous_second = -1

        while not self.account_balance:
            elapsed_time = time.time() - start_time
            current_second = int(elapsed_time)
            if current_second != previous_second:
                previous_second = current_second
            if elapsed_time >= max_attemps:
                raise QuotexTimeout(f"sending authorization with SSID {self.SSID} took too long to respond")
        return True

    async def connect(self) -> bool:
        """Method for connection to Quotex API"""
        self.ssl_Mutual_exclusion = False
        self.ssl_Mutual_exclusion_write = False
        if self.check_websocket_if_connect:
            self.close()
        ssid, self.cookies = await self.get_ssid()
        check_websocket = self.start_websocket()
        if not check_websocket:
            return check_websocket
        if not self.SSID:
            self.SSID = ssid
        return check_websocket

    def close(self) -> None:
        if self.websocket_client:
            self.websocket.close()
            self.websocket_thread.join()

    def websocket_alive(self) -> bool:
        return self.websocket_thread.is_alive()
