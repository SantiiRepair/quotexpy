<div align="center">
<img src="https://static.scarf.sh/a.png?x-pxid=cf317fe7-2188-4721-bc01-124bb5d5dbb2" />

## <img src="https://github.com/SantiiRepair/quotexpy/blob/main/.github/images/quotex-logo.png?raw=true" height="56"/>


**📈 QuotexPy is a library for interact with qxbroker easily.**

______________________________________________________________________

[![License](https://img.shields.io/badge/License-Boost_1.0-magenta.svg)](https://www.boost.org/LICENSE_1_0.txt)
[![PyPI version](https://badge.fury.io/py/quotexpy.svg)](https://badge.fury.io/py/quotexpy)
![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/pylint.yml/badge.svg)

</div>

______________________________________________________________________

## Installing

📈 QuotexPy is tested on Ubuntu 18.04 and Windows 10 with **python >= 3.10, <= 3.11.**.
```bash
pip install quotexpy
```

If you plan to code and make changes, clone and install it locally.

```bash
git clone https://github.com/SantiiRepair/quotexpy.git
pip install -e .
```

### Import
```python
from quotexpy.new import Quotex
```

### Login by email and password
```python
from quotexpy.new import Quotex

client = Quotex(email="user@email.com", password="password", browser=True)
# if connect success return True or None 
# if connect fail return False or None 
client.debug_ws_enable = False
check_connect, message = client.connect()
print(check_connect, message)
```

### Check_win & buy sample

```python
from quotexpy.new import Quotex

client = Quotex(email="user@email.com", password="password", browser=True)
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
### ⚠️ Atention 
Because cloudfare blocks requests you should enable `browser=True` to avoid `HTTP 403` errors.