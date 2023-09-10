import os
import time
import asyncio
from termcolor import colored
from quotexpy.new import Quotex


client = Quotex(
    email="diego.christ@outlook.com",
    password="@D1i2e3g4o5@Quotex",
    browser=True,
)
client.debug_ws_enable = False


async def login(attempts=2):
    check, reason = await client.connect()
    print(f"{colored('[INFO]: Connecting...', 'blue')}")
    attempt = 1
    while attempt < attempts:
        if not client.check_connect():
            print(f"Trying to reconnect, try {attempt} for {attempts}")
            check, reason = await client.connect()
            if check:
                print("Successfully reconnected!!!")
                break
            print("Error reconnecting.")
            attempt += 1
            if os.path.isfile("session.json"):
                os.remove("session.json")
        elif not check:
            attempt += 1
        else:
            break
        time.sleep(0.5)
    return check, reason


def get_balance():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        client.change_account("practice")
        print("Balance: ", client.get_balance())
        print("Exiting...")
    client.close()


def balance_refill():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        result = client.edit_practice_balance(50000)
        print(result)
    client.close()


def buy():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")
        amount = 30
        asset = "EURUSD_otc"  # "EURUSD_otc"
        direction = "call"
        duration = 10  # in seconds
        status, buy_info = client.buy(amount, asset, direction, duration)
        print(status, buy_info)
        print("Balance: ", client.get_balance())
        print("Exiting...")
    client.close()


async def buy_and_check_win():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")
        print("Balance: ", client.get_balance())
        amount = 10
        asset = "USDBRL_otc"  # "EURUSD_otc"
        direction = "call"
        duration = 5  # in seconds
        status, buy_info = client.buy(amount, asset, direction, duration)
        # print(status, buy_info)
        if status:
            print("Awaiting result...")
            if client.check_win(buy_info["id"]):
                print(f"\nWin!!! \nWe won kid!!!\nProfit: BRL {client.get_profit()}")
            else:
                print(f"\nLoss!!! \nWe lost kid!!!\nLoss: R$ {client.get_profit()}")
        else:
            print("Operation failed!!!")
        print("Balance: ", client.get_balance())
        print("Exiting...")
    client.close()


def sell_option():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")
        amount = 30
        asset = "CADCHF_otc"  # "EURUSD_otc"
        direction = "put"
        duration = 1000  # in seconds
        status, buy_info = client.buy(amount, asset, direction, duration)
        print(status, buy_info)
        client.sell_option(buy_info["id"])
        print("Balance: ", client.get_balance())
        print("Exiting...")
    client.close()


def asset_open():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        print("Check Asset Open")
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    client.close()


def get_candle():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        asset = "AUDCAD_otc"
        offset = 180  # in seconds
        period = 3600  # in seconds / opcional
        candles = client.get_candles(asset, offset, period)
        for candle in candles["data"]:
            print(candle)
    client.close()


def get_payment():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    client.close()


def get_candle_v2():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        a = client.get_candle_v2("USDJPY_otc", 10)
        print(a)
    client.close()


def get_realtime_candle():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        list_size = 10
        client.start_candles_stream("USDJPY_otc", list_size)
        while True:
            if len(client.get_realtime_candles("USDJPY_otc")) == list_size:
                break
        print(client.get_realtime_candles("USDJPY_otc"))
    client.close()


def get_signal_data():
    check_connect, message = login()
    print(check_connect, message)
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    client.close()


# get_signal_data()
# get_balance()
# get_payment()
# get_candle()
# get_candle_v2()
# get_realtime_candle()
# asset_open()
asyncio.run(buy_and_check_win())
# balance_refill()
