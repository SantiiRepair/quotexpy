import sys
import time
import random
import asyncio
import datetime
from termcolor import colored

from quotexpy import Quotex
from quotexpy.utils import asset_parse, asrun
from quotexpy.utils.account_type import AccountType
from quotexpy.utils.candles_period import CandlesPeriod
from quotexpy.utils.operation_type import OperationType


asset_current = "EURGBP"


def on_pin_code() -> str:
    code = input("Enter the code sent to your email: ")
    return code


client = Quotex(
    email="",
    password="",
    headless=True,
    on_pin_code=on_pin_code,
)


def check_asset(asset):
    asset_query = asset_parse(asset)
    asset_open = client.check_asset(asset_query)
    if not asset_open or not asset_open[2]:
        print(colored("[WARN]: ", "yellow"), "Asset is closed.")
        asset = f"{asset}_otc"
        print(colored("[WARN]: ", "yellow"), "Try OTC Asset -> " + asset)
        asset_query = asset_parse(asset)
        asset_open = client.check_asset(asset_query)
    return asset, asset_open


async def get_balance():
    check_connect = await client.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def balance_refill():
    check_connect = await client.connect()
    if check_connect:
        result = await client.edit_practice_balance(100)
        print(result)
    client.close()


async def trade():
    check_connect = await client.connect()
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
    client.close()


async def wait_for_input_exceeding_x_seconds_limit(secounds=30):
    while True:
        now = datetime.datetime.now()
        if now.second < secounds:
            return
        await asyncio.sleep(0.5)


async def trade_and_check_win():
    check_connect = await client.connect()
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
    check_connect = await client.connect()
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
    client.close()


async def assets_open():
    check_connect = await client.connect()
    if check_connect:
        for i in client.get_all_asset_name():
            print(i, client.check_asset(i))
    client.close()


async def get_payment():
    check_connect = await client.connect()
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    client.close()


async def get_candle_v2():
    check_connect = await client.connect()
    if check_connect:
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            candles = await client.get_candle_v2(asset, CandlesPeriod.ONE_MINUTE)
            print(candles)
        else:
            print(colored("[INFO]: ", "blue"), "Asset is closed.")
    client.close()


async def get_realtime_candle():
    check_connect = await client.connect()
    if check_connect:
        list_size = 10
        global asset_current
        asset, asset_open = check_asset(asset_current)
        client.start_candles_stream(asset, list_size)
        while True:
            if len(client.get_realtime_candles(asset)) == list_size:
                break
        print(client.get_realtime_candles(asset))
    client.close()


async def get_signal_data():
    check_connect = await client.connect()
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    client.close()


async def main():
    await get_balance()
    # await get_signal_data()
    # await get_payment()
    # await get_payments_payout_more_than()
    # await get_candle_v2()
    # await get_realtime_candle()
    # await assets_open()
    # await trade_and_check_win()
    # await balance_refill()


if __name__ == "__main__":
    try:
        asrun(main())
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(0)
