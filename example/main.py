import os
import time
import shutup
import random
import asyncio
import schedule
from termcolor import colored

from quotexpy.stable_api import Quotex
from quotexpy.utils import asset_parse

shutup.please()

CONST_ASSET = "AUDCAD"

def __x__(y):
    z = asyncio.get_event_loop().run_until_complete(y)
    return z


client = Quotex(email="your@mail.com", password="yourPassword")
client.debug_ws_enable = False

async def login(attempts=5):
    check, reason = await client.connect()
    print(colored("[INFO]: ", "blue"), "Start your robot")
    attempt = 1
    print(colored("[INFO]: ", "blue"), "Connecting...")
    while attempt <= attempts:
        if not client.check_connect():
            print(colored("[INFO]: ", "blue"), f"Trying to reconnect, try {attempt} for {attempts}")
            check, reason = await client.connect()
            if check:
                print(colored("[INFO]: ", "blue"), "Successfully reconnected!!!")
                break
            print(colored("[INFO]: ", "blue"), "Error reconnecting")
            attempt += 1
            if os.path.isfile("session.json"):
                os.remove("session.json")
        elif not check:
            attempt += 1
        else:
            break
        await asyncio.sleep(0.5)
    return check, reason

def check_asset(asset):
    asset_query = asset_parse(asset)
    asset_open = client.check_asset_open(asset_query)
    if not asset_open[2]:
        print(colored("[WARN]: ", "blue"), "Asset is closed.")
        asset = f"{asset}_otc"
        print(colored("[WARN]: ", "blue"), "try OTC Asset -> " + asset)
        asset_query = asset_parse(asset)
        asset_open = client.check_asset_open(asset_query)
    return asset, asset_open

async def get_balance():
    check_connect, message = await login()
    if check_connect:
        client.change_account("PRACTICE")  # "REAL"
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def balance_refill():
    check_connect, message = await login()
    if check_connect:
        result = await client.edit_practice_balance(100)
        print(result)
    client.close()


async def trade():
    check_connect, message = await login()
    if check_connect:
        client.change_account("PRACTICE")  # "REAL"
        amount = 1
        action = random.choice(["call", "put"]) # call (green), put (red)
        duration = 60  # in seconds
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            try:
                status, buy_info = await client.trade(action, amount, asset, duration)
                print(status, buy_info)
            except:
                pass
        else:
            print(colored("[WARN]: ", "blue"), "Asset is closed.")
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


lastAction = None
countSequenceLoss = 0

async def trade_and_check():
    check_connect, message = await login()
    if check_connect:
        client.change_account("PRACTICE")  # "REAL"
        balance = await client.get_balance()
        print(colored("[INFO]: ", "blue"), "Balance: ", balance)
        global lastAction
        global countSequenceLoss
        while balance >= 1:
            amount = 1
            if countSequenceLoss > 0:
                #amount = countSequenceLoss + countSequenceLoss #martigale
                amount = 2            

            if lastAction is None:
                action = random.choice(["call", "put"]) # call (green), put (red)
                lastAction = action
            else:
                action = lastAction

            duration = 60  # in seconds
            global CONST_ASSET
            asset, asset_open = check_asset(CONST_ASSET)

            if asset_open[2]:
                print(colored("[INFO]: "), "OK: Asset is open")
                status, trade_info = await client.trade(action, amount, asset, duration)
                print(status, trade_info, "\n")
                if status:
                    print(colored("[INFO]: ", "blue"), "Waiting for result...")
                    print(colored("[INFO]: ", "blue"), f"Side: {action}, countSequenceLoss: {countSequenceLoss}")
                    #print(f"id checking {trade_info[asset]['id']}")

                    if await client.check_win(asset, trade_info[asset]["id"]):
                        print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                        lastAction = action
                        countSequenceLoss = 0
                    else:
                        print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
                        countSequenceLoss += 1
                        if countSequenceLoss > 1:
                            if lastAction == "call":
                                lastAction = "put"
                            else:
                                lastAction = "call"
                            countSequenceLoss = 0
                        #else:
                    #else: #error
                    #    print(colored("[ERROR]: ", "red"), "Check Win/Loss failed!!!")
                    # lastAction = None
                else:
                    print(colored("[ERROR]: ", "red"), "Operation failed!!!")
                    #erro de tempo incorreto
                    return
            else:
                print(colored("[WARN]: ", "light_red"), "Asset is closed.")
            print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
            print(colored("[INFO]: ", "blue"), "Exiting...")
        if balance >= 1:
            pass
        else:
            print(colored("[WARN]: ", "light_red"), "No balance available :(")
    client.close()

async def sell_option():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")#"REAL"
        amount = 30
        #asset = "EURUSD_otc"  # "EURUSD_otc"
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        direction = "put"
        duration = 1000  # in seconds
        status, buy_info = await client.trade(amount, asset, direction, duration)
        print(status, buy_info)
        await client.sell_option(buy_info["id"])
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def assets_open():
    check_connect, message = await login()
    if check_connect:
        print("Check Asset Open")
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    client.close()


async def get_candle():
    check_connect, message = await login()
    if check_connect:
        #asset = "AUDCAD_otc"
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        offset = 180  # in seconds
        period = 3600  # in seconds / opcional
        candles = await client.get_candles(asset, offset, period)
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

import datetime
#import numpy as np
async def get_candle_v2():
    check_connect, message = await login()
    print(check_connect, message)
    period = 1
    size = 50
    if check_connect:
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        candles = await client.get_candle_v2(asset, period, size)
        #data = np.array(candles)
        ## Adiciona uma nova coluna com os valores convertidos em data
        #timestamps = data[:, 0]
        #datas = [datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M:%S') for ts in timestamps]
        #new_column = np.array(datas).reshape(-1, 1)
        #data_with_dates = np.hstack((data, new_column))

        for candle in candles:
            print(candle)
            timestamp = candle[0]
            data = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')
            print(data)
    client.close()


async def get_realtime_candle():
    check_connect, message = await login()
    if check_connect:
        list_size = 10
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        client.start_candles_stream(asset, list_size)
        while True:
            if len(client.get_realtime_candles(asset)) == list_size:
                break
        print(client.get_realtime_candles(asset))
    client.close()


async def get_signal_data():
    check_connect, message = await login()
    if check_connect:
        while True:
            print(client.get_signal_data())
            time.sleep(1)
    client.close()


async def get_moving_average():
    periods = 21
    interval = "1m"
    symbol = "AUDCAD=X"
    await client.get_moving_average(symbol=symbol, interval=interval, periods=periods)
    lastCandles = await client.get_last_candles(symbol=symbol, interval=interval)
    print(lastCandles)


async def main():
    # await get_balance()
    # await get_signal_data()
    # await get_payment()
    #await get_candle()
    #await get_candle_v2()
    #await get_realtime_candle()
    # await assets_open()
    await trade_and_check()
    # await balance_refill()
    # await get_moving_average()


def run_main():
    __x__(main())

#Agendamentos:
schedule.every(30).seconds.do(run_main)

while True:
    schedule.run_pending()
    time.sleep(1)
