import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class Navigator(object):
    def __init__(self, api):
        """Tools for quotexpy navigation."""
        self.base_url = "qxbroker.com"
        self.https_base_url = f"https://{self.base_url}"

        self.api = api
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504, 104],
            allowed_methods=["HEAD", "POST", "PUT", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def send_request(self, method: str, url: str, headers: dict, **kwargs):
        return self.session.request(method, url, headers=headers, **kwargs)
