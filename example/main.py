import sys
import time
import random
import asyncio
import datetime
from pathlib import Path
from termcolor import colored

from quotexpy import Quotex
from quotexpy.utils.account_type import AccountType
from quotexpy.utils.operation_type import OperationType
from quotexpy.utils import asset_parse, sessions_file_path

asset_current = "EURUSD"


def pin_code_handler() -> str:
    code = input("Enter the code sent to your email: ")
    return code


class SingletonDecorator:
    """
    A decorator that turns a class into a singleton.
    """

    def __init__(self, cls):
        self.cls = cls
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance is None:
            self.instance = self.cls(*args, **kwargs)
        return self.instance


@SingletonDecorator
class MyConnection:
    """
    This class represents a connection object and provides methods for connecting to a client.
    """

    def __init__(self, client_instance: Quotex):
        self.client = client_instance

    async def connect(self, attempts=5):
        check = await self.client.connect()
        if not check:
            attempt = 0
            while attempt <= attempts:
                if not self.client.check_connect():
                    check = await self.client.connect()
                    if check:
                        print("Reconectado com sucesso!!!")
                        break
                    print("Erro ao reconectar.")
                    attempt += 1
                    if Path(sessions_file_path).is_file():
                        Path(sessions_file_path).unlink()
                    print(f"Tentando reconectar, tentativa {attempt} de {attempts}")
                elif not check:
                    attempt += 1
                else:
                    break
                await asyncio.sleep(5)
            return check
        return check

    def close(self):
        """
        Closes the client connection.
        """
        self.client.close()


def run(y):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    z = loop.run_until_complete(y)
    return z


client = Quotex(
    email="",
    password="",
    on_pin_code=pin_code_handler,
)

client.debug_ws_enable = False


def check_asset(asset):
    asset_query = asset_parse(asset)
    asset_open = client.check_asset_open(asset_query)
    if not asset_open or not asset_open[2]:
        print(colored("[WARN]: ", "yellow"), "Asset is closed.")
        asset = f"{asset}_otc"
        print(colored("[WARN]: ", "yellow"), "Try OTC Asset -> " + asset)
        asset_query = asset_parse(asset)
        asset_open = client.check_asset_open(asset_query)
    return asset, asset_open


async def get_balance():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)  # "REAL"
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    prepare_connection.close()


async def balance_refill():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        result = await client.edit_practice_balance(100)
        print(result)
    prepare_connection.close()


async def trade():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        amount = 1
        action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            try:
                await client.trade(action, amount, asset, 60)
            except:
                pass
        else:
            print(colored("[WARN]: ", "yellow"), "Asset is closed.")
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    prepare_connection.close()


async def wait_for_input_exceeding_x_seconds_limit(secounds=30):
    while True:
        now = datetime.datetime.now()
        if now.second < secounds:
            return
        await asyncio.sleep(0.5)


async def trade_and_check_win():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        amount = 50
        asset, asset_open = check_asset(asset_current)
        await wait_for_input_exceeding_x_seconds_limit(30)  # waiting for seconds
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
            status, trade_info = await client.trade(action, amount, asset, 60)
            if status:
                print(colored("[INFO]: ", "blue"), "Waiting for result...")
                if await client.check_win(trade_info.get("id")):
                    print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                else:
                    print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
            else:
                print(colored("[WARN]: ", "light_red"), "Operation not realized.")
        else:
            print(colored("[WARN]: ", "light_red"), "Asset is closed.")
        time.sleep(2)
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
    print(colored("[INFO]: ", "blue"), "Exiting...")


async def sell_option():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        amount = 30
        global asset_current
        asset, asset_open = check_asset(asset_current)
        direction = OperationType.PUT_RED
        duration = 1000  # in seconds
        status, buy_info = await client.trade(amount, asset, direction, duration)
        await client.sell_option(buy_info["id"])
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    prepare_connection.close()


async def assets_open():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    prepare_connection.close()


async def get_payment():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    prepare_connection.close()


# import numpy as np
async def get_candle_v2():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    period = 100
    if check_connect:
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            # 60 at 180 seconds
            candles = await client.get_candle_v2(asset, period)
            print(candles)
        else:
            print(colored("[INFO]: ", "blue"), "Asset is closed.")
    prepare_connection.close()


async def get_realtime_candle():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        list_size = 10
        global asset_current
        asset, asset_open = check_asset(asset_current)
        client.start_candles_stream(asset, list_size)
        while True:
            if len(client.get_realtime_candles(asset)) == list_size:
                break
        print(client.get_realtime_candles(asset))
    prepare_connection.close()


async def get_signal_data():
    prepare_connection = MyConnection(client)
    check_connect = await prepare_connection.connect()
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    prepare_connection.close()


async def main():
    # await get_balance()
    # await get_signal_data()
    # await get_payment()
    # await get_payments_payout_more_than()
    # await get_candle_v2()
    # await get_realtime_candle()
    # await assets_open()
    await trade_and_check_win()
    # await balance_refill()


if __name__ == "__main__":
    try:
        run(main())
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(0)
