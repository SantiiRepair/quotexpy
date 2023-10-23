import os
import time
import shutup
from termcolor import colored
from quotexpy.new import Quotex
from asyncio import get_event_loop

shutup.please()


def __x__(y):
    z = get_event_loop().run_until_complete(y)
    return z


client = Quotex(
    email="...@gmail.com",
    password="...",
    browser=True,
)
client.debug_ws_enable = False


async def login(attempts=8):
    attempt = 1
    print(colored("[INFO]: ", "blue"), "Connecting...")
    while attempt < attempts:
        check, reason = await client.connect()
        if not client.check_connect():
            print(colored("[INFO]: ", "blue"), f"Trying to reconnect, try {attempt} for {attempts}")
            check, reason = await client.connect()
            if check:
                print(colored("[INFO]: ", "blue"), "Successfully reconnected!!!")
                break
            print(colored("[INFO]: ", "blue"), "Error reconnecting")
            attempt += 1
            if os.path.isfile(".session.json"):
                os.remove(".session.json")
        elif not check:
            attempt += 1
        else:
            break
        time.sleep(0.5)
    return check, reason


async def get_balance():
    check_connect, message = await login()
    if check_connect:
        client.change_account("practice")
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def balance_refill():
    check_connect, message = await login()
    if check_connect:
        result = client.edit_practice_balance(50000)
        print(result)
    client.close()


async def trade():
    check_connect, message = await login()
    if check_connect:
        client.change_account("PRACTICE")
        amount = 30
        asset = "EURUSD_otc"  # "EURUSD"
        action = "call"  # call (green), put (red)
        duration = 60  # in seconds
        status, buy_info = client.trade(action, amount, asset, duration)
        print("Balance: ", client.get_balance())
        print("Exiting...")
    client.close()


async def trade_and_check():
    check_connect, message = await login()
    if check_connect:
        client.change_account("PRACTICE")
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        amount = 10
        asset = "EURUSD_otc"  # "EURUSD"
        action = "call"  # call (green), put (red)
        duration = 60  # in seconds
        status, buy_info = client.trade(action, amount, asset, duration)
        if status:
            if client.check_win(buy_info["id"]):
                print(f"\nWin!!! \nProfit: {client.get_profit()}")
            else:
                print(f"\nLoss!!! \nLoss: {client.get_profit()}")
        else:
            print(colored("[ERROR]: ", "red"), "Operation failed!!!")
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def asset_open():
    check_connect, message = await login()
    if check_connect:
        print("Check Asset Open")
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    client.close()


async def get_candle():
    check_connect, message = await login()
    if check_connect:
        asset = "AUDCAD_otc"
        offset = 180  # in seconds
        period = 3600  # in seconds / opcional
        candles = client.get_candles(asset, offset, period)
        for candle in candles["data"]:
            print(candle)
    client.close()


async def get_payment():
    check_connect, message = await login()
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    client.close()


async def get_candle_v2():
    check_connect, message = await login()
    if check_connect:
        a = client.get_candle_v2("USDJPY_otc", 10)
        print(a)
    client.close()


async def get_realtime_candle():
    check_connect, message = await login()
    if check_connect:
        list_size = 10
        client.start_candles_stream("USDJPY_otc", list_size)
        while True:
            if len(client.get_realtime_candles("USDJPY_otc")) == list_size:
                break
        print(client.get_realtime_candles("USDJPY_otc"))
    client.close()


async def get_signal_data():
    check_connect, message = await login()
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    client.close()


# __x__(get_signal_data())
# __x__(get_balance())
# __x__(get_payment())
# __x__(get_candle())
# __x__(get_candle_v2())
# __x__(get_realtime_candle())
# __x__(asset_open())
__x__(trade_and_check())
# __x__(balance_refill())
