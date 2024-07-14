import json
import time


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
