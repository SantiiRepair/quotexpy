import os
import json
import time
import typing
import asyncio


def asset_parse(asset):
    new_asset = asset[:3] + "/" + asset[3:]
    if "_otc" in asset:
        asset = new_asset.replace("_otc", " (OTC)")
    else:
        asset = new_asset
    return asset


def unix_time() -> int:
    return int(time.time())


def is_valid_json(mj):
    try:
        json.loads(mj)
    except ValueError as _:
        return False
    return True


def asrun(x: typing.Coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = loop.run_until_complete(x)
    return r


home_dir = os.path.expanduser("~")
log_file_path = os.path.join(home_dir, ".quotexpy.log")
sessions_file_path = os.path.join(home_dir, ".sessions.pkl")
