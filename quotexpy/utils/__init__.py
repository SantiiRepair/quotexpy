import os
import json
import time
import random
import string
import typing
import asyncio
from collections import defaultdict


class __MParser:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    return defaultdict(lambda: nested_dict(n - 1, type))


def asset_parse(asset: str):
    new_asset = f"{asset[:3]}/{asset[3:]}"
    if "_otc" in asset:
        return new_asset.replace("_otc", " (OTC)")
    return new_asset


def request_id() -> str:
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    random_string = "".join(random.choice(characters) for _ in range(20))
    return random_string


def unix_time() -> int:
    return int(time.time())


def is_valid_json(x: typing.Any):
    try:
        json.loads(x)
    except ValueError as _:
        return False
    return True


def parse_dict(data: typing.Any) -> typing.Optional[__MParser]:
    """Parse a dictionary into an instance of __MParser.

    Args:
        data (Any): The input data to parse.

    Returns:
        Optional[__MParser]: An instance of __MParser if the input is a dictionary,
        otherwise None.
    """
    if isinstance(data, dict):
        return __MParser(**data)
    return None


def asrun(x: typing.Coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    r = loop.run_until_complete(x)
    return r


home_dir = os.path.expanduser("~")
cert_path = os.path.join(home_dir, "cacert.pem")
log_file_path = os.path.join(home_dir, ".quotexpy.log")
sessions_file_path = os.path.join(home_dir, ".sessions.pkl")
