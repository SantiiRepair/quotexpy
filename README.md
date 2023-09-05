<div align="center">
<img src="https://static.scarf.sh/a.png?x-pxid=cf317fe7-2188-4721-bc01-124bb5d5dbb2" />

## <img src="https://github.com/SantiiRepair/quotexpy/blob/main/.github/images/quotex-logo.png?raw=true" height="56"/>


**QuotexPy is a library for interact with qxbroker easily.**

______________________________________________________________________

[![License](<https://img.shields.io/badge/License-BSL%1.0-brightgreen.svg>)](https://opensource.org/licenses/MPL-2.0)
[![PyPI version](https://badge.fury.io/py/quotexpy.svg)](https://badge.fury.io/py/quotexpy)
[![DOI](https://zenodo.org/badge/265612440.svg)](https://zenodo.org/badge/latestdoi/265612440)

![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/pylint.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/data_tests.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/docker.yaml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/inference_tests.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/style_check.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/text_tests.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/tts_tests.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/vocoder_tests.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/zoo_tests0.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/zoo_tests1.yml/badge.svg)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/zoo_tests2.yml/badge.svg)

</div>

______________________________________________________________________

## Installing

🐸TTS is tested on Ubuntu 18.04 with **python >= 3.10, <= 3.11.**.
```bash
pip install quotex-py
```

If you plan to code and make changes, clone and install it locally.

```bash
git clone https://github.com/SantiiRepair/quotexpy.git
pip install -e .
```

### Import
```python
from quotexpy.stable.new import Quotex
```

### Login by email and password
if connect sucess return True,None  

if connect fail return False,None  
```python
from quotexpy.stable.new import Quotex

client = Quotex(email="user@gmail.com", password="pwd")
client.debug_ws_enable = False
check_connect, message = client.connect()
print(check_connect, message)
```

### Check_win & buy sample

```python
from quotexpy.stable.new import Quotex

client = Quotex(email="user@gmail.com", password="pwd")
client.debug_ws_enable = False
check_connect, message = client.connect()
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
```
