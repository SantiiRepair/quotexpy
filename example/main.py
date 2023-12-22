import os
import sys
import time
import datetime
import shutup
import random
import asyncio
import schedule
from termcolor import colored

from quotexpy import Quotex
from quotexpy.utils import asset_parse
from quotexpy.utils.account_type import AccountType
from quotexpy.utils.operation_type import OperationType
from quotexpy.utils.duration_time import DurationTime
from my_connection import MyConnection

shutup.please()

asset_current = "AUDCAD"

def __x__(y):
    z = asyncio.get_event_loop().run_until_complete(y)
    return z

client = Quotex(email="your@email.com", password="yourPassord")
client.debug_ws_enable = False

def check_asset(asset):
    asset_query = asset_parse(asset)
    asset_open = client.check_asset_open(asset_query)
    if not asset_open[2]:
        print(colored("[WARN]: ", "yellow"), "Asset is closed.")
        asset = f"{asset}_otc"
        print(colored("[WARN]: ", "yellow"), "Try OTC Asset -> " + asset)
        asset_query = asset_parse(asset)
        asset_open = client.check_asset_open(asset_query)
    return asset, asset_open

async def get_balance():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)  # "REAL"
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    prepare_connection.close()

async def balance_refill():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        result = await client.edit_practice_balance(100)
        print(result)
    prepare_connection.close()

async def trade():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        amount = 1
        action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            try:
                await client.trade(action, amount, asset, DurationTime.ONE_MINUTE)
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
            return  # Returns when it's the right time to proceed
        await asyncio.sleep(0.5)

async def trade_and_check_win():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    #check_connect, message = await connect()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())        
        amount = 50
        asset, asset_open = check_asset(asset_current)
        await wait_for_input_exceeding_x_seconds_limit(30) #waiting for seconds
        if asset_open[2]:
            print("OK: Asset está aberto.")
            action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
            status, trade_info = await client.trade(
                   action, amount, asset, DurationTime.ONE_MINUTE
                )
            print(status, trade_info, "\n")
            if status:
                print(colored("[INFO]: ", "blue"), "Waiting for result...")
                if await client.check_win(trade_info["id"]):
                    print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                else:
                    print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
            else:
                print(colored("[WARN]: ", "light_red"), "Operation not realized.")
        else:
            print(colored("[WARN]: ", "light_red"), "Asset is closed.")
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
    print(colored("[INFO]: ", "blue"), "Exiting...")
    print("Saindo...")        

async def sell_option():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    print(check_connect, message)
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        amount = 30
        global asset_current
        asset, asset_open = check_asset(asset_current)
        direction = OperationType.PUT_RED
        duration = 1000  # in seconds
        status, buy_info = await client.trade(amount, asset, direction, duration)
        print(status, buy_info)
        await client.sell_option(buy_info["id"])
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    prepare_connection.close()


async def assets_open():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        print("Check Asset Open")
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    prepare_connection.close()


async def get_payment():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    prepare_connection.close()

# import numpy as np
async def get_candle_v2():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
    print(check_connect, message)
    period = 100    
    if check_connect:
        global asset_current
        asset, asset_open = check_asset(asset_current)
        if asset_open[2]:
            print("OK: Asset está aberto.")
            # 60 at 180 seconds
            candles = await client.get_candle_v2(asset, period)
            print(candles)
        else:
            print("ERRO: Asset está fechado.")
    prepare_connection.close()


async def get_realtime_candle():
    prepare_connection = MyConnection(client)
    check_connect, message = await prepare_connection.connect()
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
    check_connect, message = await prepare_connection.connect()
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    prepare_connection.close()

async def main():
    # await get_balance()
    # await get_signal_data()
    #await get_payment()
    #await get_payments_payout_more_than()
    #await get_candle_v2()
    # await get_realtime_candle()
    #await assets_open()
    await trade_and_check_win()    
    # await balance_refill()    

def run_main():
    try:
        __x__(main())
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(0)

# Agendamentos:
schedule.every(1).seconds.do(run_main)

while True:
    schedule.run_pending()
    time.sleep(5)
