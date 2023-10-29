import os
import time
import shutup
import random
from termcolor import colored
import asyncio
import schedule
from quotexpy.stable_api import Quotex
from asyncio import get_event_loop
from quotexpy.utils import asset_parse

shutup.please()

def __x__(y):
    z = get_event_loop().run_until_complete(y)
    return z

client = Quotex(
    email="your@email.com",
    password="yourpassword"
)
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


async def get_balance():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")  # "REAL"
        print(colored("[INFO]: ", "blue"), "Balance: ", client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()


async def balance_refill():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        result = await client.edit_practice_balance(1000)
        print(result)
    client.close()


async def trade():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")#"REAL"
        amount = 1
        asset = "AUDCAD"  # "AUDCAD_otc"
        #action = "call"  # call (green), put (red)
        action = random.choice(["call", "put"]) # call (green), put (red)
        duration = 60  # in seconds
        asset_query = asset_parse(asset)
        asset_open = client.check_asset_open(asset_query)
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

async def trade_and_check():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")#"REAL"
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        amount = 1
        action = random.choice(["call", "put"]) # call (green), put (red)
        #horario negociacao 09:00 as 15:00 fora isto é otc
        #nao opera sabado e domingo, só otc
        asset = "AUDCAD_otc"  # "EURUSD_otc"
        duration = 60  # in seconds
        asset_query = asset_parse(asset)
        asset_open = client.check_asset_open(asset_query)
        if asset_open[2]:
            print(colored("[INFO]: "), "OK: Asset is open")
            status, buy_info = await client.trade(action, amount, asset, duration)
            print(status, buy_info, "\n")
            if status:
                print(colored("[INFO]: ", "blue"), "Waiting for result...")
                if await client.check_win(buy_info[asset]["id"]):
                    print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                else:
                    print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
            else:
                print(colored("[ERROR]: ", "red"), "Operation failed!!!")
        else:
            print(colored("[WARN]: ", "red"), "Asset is closed.")
        print(colored("[INFO]: ", "blue"), "Balance: ", await client.get_balance())
        print(colored("[INFO]: ", "blue"), "Exiting...")
    client.close()

async def sell_option():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        client.change_account("PRACTICE")#"REAL"
        amount = 30
        asset = "EURUSD_otc"  # "EURUSD_otc"
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
    print(check_connect, message)
    if check_connect:
        print("Check Asset Open")
        for i in client.get_all_asset_name():
            print(i, client.check_asset_open(i))
    client.close()


async def get_candle():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        asset = "AUDCAD_otc"
        offset = 180  # in seconds
        period = 3600  # in seconds / opcional
        candles = await client.get_candles(asset, offset, period)
        for candle in candles["data"]:
            print(candle)
    client.close()


async def get_payment():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    client.close()


async def get_candle_v2():
    check_connect, message = await login()
    print(check_connect, message)
    if check_connect:
        candles = await client.get_candle_v2("USDJPY", 180)
        print(candles)
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
# __x__(assets_open())
#__x__(trade_and_check())
# __x__(balance_refill())

async def main():
    #await get_balance()
    #await get_signal_data()
    # await get_payment()
    # await get_candle()
    #await get_candle_v2()
    # await get_realtime_candle()
    # await assets_open()
    # await buy()
    await trade_and_check()
    # await balance_refill()

#if __name__ == "__main__":
def run_main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #loop.run_forever()

#Agendamentos:
schedule.every(20).seconds.do(run_main)

while True:
    schedule.run_pending()
    time.sleep(1)
