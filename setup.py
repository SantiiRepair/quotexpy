# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quotexpy',
 'quotexpy.http',
 'quotexpy.utils',
 'quotexpy.ws',
 'quotexpy.ws.channels',
 'quotexpy.ws.objects']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'beautifulsoup4>=4.11.2,<5.0.0',
 'certifi>=2022.12.7,<2023.0.0',
 'charset-normalizer>=3.2.0,<4.0.0',
 'cloudscraper>=1.2.71,<2.0.0',
 'greenlet>=2.0.2,<3.0.0',
 'idna>=3.4,<4.0',
 'importlib-metadata>=6.2.0,<7.0.0',
 'playwright>=1.37.0,<2.0.0',
 'pyee>=9.0.4,<10.0.0',
 'pyparsing>=3.1.1,<4.0.0',
 'requests-toolbelt>=1.0.0,<2.0.0',
 'requests>=2.31.0,<3.0.0',
 'shutup>=0.2.0,<0.3.0',
 'simplejson>=3.18.3,<4.0.0',
 'soupsieve>=2.4,<3.0',
 'termcolor>=2.3.0,<3.0.0',
 'tqdm>=4.65.0,<5.0.0',
 'typing_extensions>=4.5.0,<5.0.0',
 'urllib3>=2.0.5,<3.0.0',
 'websocket-client>=1.6.3,<2.0.0',
 'websockets>=11.0.3,<12.0.0',
 'zipp>=3.17.0,<4.0.0']

setup_kwargs = {
    'name': 'quotexpy',
    'version': '1.0.38',
    'description': '📈 QuotexPy is a library for interact with qxbroker easily.',
    'long_description': '<div align="center">\n<img src="https://static.scarf.sh/a.png?x-pxid=cf317fe7-2188-4721-bc01-124bb5d5dbb2" />\n\n## <img src="https://github.com/SantiiRepair/quotexpy/blob/main/.github/images/quotex-logo.png?raw=true" height="56"/>\n\n\n**📈 QuotexPy is a library for interact with qxbroker easily.**\n\n______________________________________________________________________\n\n[![License](https://img.shields.io/badge/License-GPL--3.0-magenta.svg)](https://www.gnu.org/licenses/gpl-3.0.txt)\n[![PyPI version](https://badge.fury.io/py/quotexpy.svg)](https://badge.fury.io/py/quotexpy)\n![GithubActions](https://github.com/SantiiRepair/quotexpy/actions/workflows/pylint.yml/badge.svg)\n\n</div>\n\n______________________________________________________________________\n\n## Installing\n\n📈 QuotexPy is tested on Ubuntu 18.04 and Windows 10 with **python >= 3.10, <= 3.11.**.\n```bash\npip install quotexpy\n```\n\nIf you plan to code and make changes, clone and install it locally.\n\n```bash\ngit clone https://github.com/SantiiRepair/quotexpy.git\npip install -e .\n```\n\n### Import\n```python\nfrom quotexpy.new import Quotex\n```\n\n### Login by email and password\n```python\nfrom quotexpy.new import Quotex\n\nclient = Quotex(email="user@email.com", password="password", browser=True)\n# if connect success return True or None \n# if connect fail return False or None \nclient.debug_ws_enable = False\ncheck_connect, message = client.connect()\nprint(check_connect, message)\n```\n\n### Check_win & buy sample\n\n```python\nfrom quotexpy.new import Quotex\n\nclient = Quotex(email="user@email.com", password="password", browser=True)\nclient.debug_ws_enable = False\ncheck_connect, message = client.connect()\nprint(check_connect, message)\nif check_connect:\n    client.change_account("PRACTICE")\n    amount = 30\n    asset = "EURUSD_otc"  # "EURUSD_otc"\n    direction = "call"\n    duration = 10  # in seconds\n    status, buy_info = client.buy(amount, asset, direction, duration)\n    print(status, buy_info)\n    print("Balance: ", client.get_balance())\n    print("Exiting...")\nclient.close()\n```\n### ⚠️ Atention \nBecause cloudfare blocks requests you should enable `browser=True` to avoid `HTTP 403` errors.\n',
    'author': 'Santiago Ramirez',
    'author_email': 'santiirepair@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/SantiiRepair/quotexpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

