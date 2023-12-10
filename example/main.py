import os
import time
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

shutup.please()

CONST_ASSET = "AUDCAD"

# vars global parameters
last_action = None
count_sequence_loss = 1
is_trade_open = False
# countSequenceLossTrend = 0

# management risk
valor_entrada_em_operacao = 2  # dollars
valor_entrada_inicial = valor_entrada_em_operacao
limite_wins_sequencias = 2
limite_tentativas_recuperacao_loss_gale = 2
count_gale = 0
count_win = 0
count_loss = 0
count_loss_print = 0
count_win_print = 0
lucro = 0
valor_total_debito_loss = 0
valor_total_credito_win = 0
##--end management risk--##


def __x__(y):
    z = asyncio.get_event_loop().run_until_complete(y)
    return z


client = Quotex(email="user@gmail.com", password="password")
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
            if os.path.isfile(".session.json"):
                os.remove(".session.json")
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
        client.change_account(AccountType.PRACTICE)  # "REAL"
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
        client.change_account(AccountType.PRACTICE)
        amount = 1
        action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        if asset_open[2]:
            print(colored("[INFO]: ", "blue"), "Asset is open.")
            try:
                status, buy_info = await client.trade(action, amount, asset, DurationTime.ONE_MINUTE)
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
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        balance = await client.get_balance()
        print(colored("[INFO]: ", "blue"), "Balance: ", balance)
        global last_action
        global count_sequence_loss
        while balance >= 1:
            amount = 1
            if count_sequence_loss > 0:
                # amount = countSequenceLoss + countSequenceLoss #martigale
                amount = 2

            if last_action is None:
                action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
                last_action = action
            else:
                action = last_action

            global CONST_ASSET
            asset, asset_open = check_asset(CONST_ASSET)

            if asset_open[2]:
                print(colored("[INFO]: "), "OK: Asset is open")
                status, trade_info = await client.trade(action, amount, asset, DurationTime.ONE_MINUTE)
                # print(status, trade_info, "\n")
                if status:
                    print(colored("[INFO]: ", "blue"), "Waiting for result...")
                    print(colored("[INFO]: ", "blue"), f"Side: {action}, countSequenceLoss: {count_sequence_loss}")
                    # print(f"id checking {trade_info[asset]['id']}")

                    if await client.check_win(asset, trade_info[asset]["id"]):
                        print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                        last_action = action
                        count_sequence_loss = 0
                    else:
                        print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
                        count_sequence_loss += 1
                        if count_sequence_loss > 1:
                            if last_action == OperationType.CALL_GREEN:
                                last_action = OperationType.PUT_RED
                            else:
                                last_action = OperationType.CALL_GREEN
                            count_sequence_loss = 0
                        # else:
                    # else: #error
                    #    print(colored("[ERROR]: ", "red"), "Check Win/Loss failed!!!")
                    # lastAction = None
                else:
                    print(colored("[ERROR]: ", "red"), "Operation failed!!!")
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


async def management_risk(result_trade):
    global valor_entrada_em_operacao
    global valor_entrada_inicial
    global limite_wins_sequencias
    global limite_tentativas_recuperacao_loss_gale
    global lucro
    global count_loss
    global count_loss_print
    global count_win
    global count_win_print
    global valor_total_credito_win
    global valor_total_debito_loss
    global count_gale

    if result_trade:  # win
        valor_total_credito_win = valor_total_credito_win + valor_entrada_em_operacao
        count_win = count_win + 1
        count_loss = 0
        count_win_print = count_win_print + 1

        #Se tiver 2 wins seguidos reseta entrada
        if count_win == limite_wins_sequencias:
            valor_entrada_em_operacao = valor_entrada_inicial
            print(f'\nLimite de Wins atingido: {count_win}\nReinicia o valor de entrada --> Entrada atual: {valor_entrada_em_operacao}')
            count_gale = 0
            count_win = 0
            lucro = round (valor_total_debito_loss + valor_total_credito_win,2)
            print(f'\nPróxima entrada: {valor_entrada_em_operacao}\nLucro atual: {lucro}\nWins: {count_win_print}\nLoss: {count_loss_print}\n')
        else:
            count_gale += 1

            valor_entrada_em_operacao = round(valor_entrada_em_operacao * 1,2)
            lucro = round (valor_total_debito_loss + valor_total_credito_win,2) #new
            print(f'\nPróxima entrada: {valor_entrada_em_operacao}\nLucro atual: {lucro}\nWins: {count_win_print}\nLoss: {count_loss_print}\n')
            print(f'\nSequencia de gale no win: {count_gale} --> Repetindo o valor da entrada: {valor_entrada_em_operacao}\n')

        #Verifica se o valor da entrada é menor que o valor inicial
        if valor_entrada_em_operacao < valor_entrada_inicial:
            valor_entrada_em_operacao = valor_entrada_inicial
            print(f'\nReiniciando o valor da entrada para: {valor_entrada_em_operacao} --> MOTIVO: Entrada atual < Entrada inicial')

    #Qndo der loss mantém o valor
    #Próxima entrada = entrada inicial
    if not result_trade: #loss
        valor_total_debito_loss = valor_total_debito_loss - valor_entrada_em_operacao
        count_loss = count_loss + 1
        count_loss_print = count_loss_print + 1
        #valor_entrada_em_operacao = valor_entrada_inicial (reinicia entrada apos loss)
        valor_entrada_em_operacao = round(valor_entrada_em_operacao * 1.5,2) #Dobra quando da loss
        count_gale = count_gale + 1
        count_win = 0
        #Painel de resultados
        #entrada_em_operacao = round(entrada_em_operacao,2)
        lucro = round (valor_total_debito_loss + valor_total_credito_win,2)

        print(f'\nPróxima entrada: {valor_entrada_em_operacao}\nLucro atual: {lucro}\nWins: {count_win_print}\nLoss: {count_loss_print}\n')


async def wait_for_input_exceeding_30_seconds_limit():
    while True:
        now = datetime.datetime.now()
        if now.second < 30:
            return  # Returns when it's the right time to proceed
        await asyncio.sleep(0.5)


async def strategy_random():
    check_connect, message = await login()
    if check_connect:
        client.change_account(AccountType.PRACTICE)
        balance = await client.get_balance()
        print(colored("[INFO]: ", "blue"), "Balance: ", balance)
        global last_action
        global count_sequence_loss
        global count_gale
        global valor_entrada_em_operacao
        global is_trade_open

        while balance >= 1:
            if last_action is None:
                action = random.choice([OperationType.CALL_GREEN, OperationType.PUT_RED])
                last_action = action
            else:
                action = last_action

            global CONST_ASSET
            asset, asset_open = check_asset(CONST_ASSET)

            await wait_for_input_exceeding_30_seconds_limit()

            if asset_open[2] and not is_trade_open:
                print(colored("[INFO]: "), "OK: Asset is open")
                status, trade_info = await client.trade(
                    action, valor_entrada_em_operacao, asset, DurationTime.ONE_MINUTE
                )
                print(status, trade_info, "\n")
                if status:
                    is_trade_open = True
                    print(colored("[INFO]: ", "blue"), "Waiting for result...")
                    print(colored("[INFO]: ", "blue"), f"Side: {action}")
                    result_trade = await client.check_win(asset, trade_info[asset]["id"])
                    if result_trade:
                        is_trade_open = False
                        print(colored("[INFO]: ", "green"), f"Win -> Profit: {client.get_profit()}")
                        last_action = action
                        count_sequence_loss = 0
                    else:
                        is_trade_open = False
                        print(colored("[INFO]: ", "light_red"), f"Loss -> Loss: {client.get_profit()}")
                        count_sequence_loss += 1
                        count_gale += 1
                        if count_sequence_loss > 1:
                            if last_action == OperationType.CALL_GREEN:
                                last_action = OperationType.PUT_RED
                            else:
                                last_action = OperationType.CALL_GREEN
                            count_sequence_loss = 0
                    await management_risk(result_trade=result_trade)
                else:
                    if is_trade_open:
                        print(colored("[INFO]: ", "blue"), "Trade in progress. Not permited open new trade. waiting current operation.")
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
        client.change_account(AccountType.PRACTICE)
        amount = 30
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        direction = OperationType.PUT_RED
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


async def get_payment():
    check_connect, message = await login()
    if check_connect:
        all_data = client.get_payment()
        for asset_name in all_data:
            asset_data = all_data[asset_name]
            print(asset_name, asset_data["payment"], asset_data["open"])
    client.close()


import datetime


# import numpy as np
async def get_candle_v2():
    check_connect, message = await login()
    print(check_connect, message)
    period = 1
    size = 50
    if check_connect:
        global CONST_ASSET
        asset, asset_open = check_asset(CONST_ASSET)
        candles = await client.get_candle_v2(asset, period, size)
        # data = np.array(candles)
        ## Adiciona uma nova coluna com os valores convertidos em data
        # timestamps = data[:, 0]
        # datas = [datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y %H:%M:%S') for ts in timestamps]
        # new_column = np.array(datas).reshape(-1, 1)
        # data_with_dates = np.hstack((data, new_column))

        for candle in candles:
            print(candle)
            timestamp = candle[0]
            data = datetime.datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
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


async def main():
    # await get_balance()
    # await get_signal_data()
    # await get_payment()
    # await get_candle_v2()
    # await get_realtime_candle()
    # await assets_open()
    # await trade_and_check()
    await strategy_random()
    # await balance_refill()


def run_main():
    __x__(main())


# Agendamentos:
schedule.every(30).seconds.do(run_main)

while True:
    schedule.run_pending()
    time.sleep(1)
