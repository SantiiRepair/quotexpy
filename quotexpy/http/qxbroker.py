import re
import json
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Tuple, Any
import undetected_chromedriver as uc
from quotexpy.exceptions import QuotexAuthError


class Browser(object):
    email = None
    password = None
    headless = None

    base_url = "qxbroker.com"
    https_base_url = f"https://{base_url}"

    def __init__(self, api):
        self.api = api

    def get_cookies_and_ssid(self) -> Tuple[Any, str]:
        try:
            self.browser = uc.Chrome(headless=self.headless, use_subprocess=False)
        except TypeError as exc:
            raise SystemError("Chrome is not installed, did you forget?") from exc
        self.browser.get(f"{self.https_base_url}/en/sign-in")
        if self.browser.current_url != f"{self.https_base_url}/en/trade":
            self.browser.execute_script('document.getElementsByName("email")[1].value = arguments[0];', self.email)
            self.browser.execute_script(
                'document.getElementsByName("password")[1].value = arguments[0];', self.password
            )
            self.browser.execute_script(
                """document.evaluate("//div[@id='tab-1']/form", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.submit();"""
            )

            time.sleep(5)
        cookies = self.browser.get_cookies()
        self.api.cookies = cookies
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        user_agent = self.browser.execute_script("return navigator.userAgent;")
        self.api.user_agent = user_agent
        try:
            script: str = soup.find_all("script", {"type": "text/javascript"})[1].get_text()
        except Exception as exc:
            raise QuotexAuthError("incorrect username or password") from exc
        match = re.sub("window.settings = ", "", script.strip().replace(";", ""))

        dx: dict = json.loads(match)
        ssid = dx.get("token")
        output_file = Path(".session.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)
        cookiejar = requests.utils.cookiejar_from_dict({c["name"]: c["value"] for c in cookies})
        cookie_string = "; ".join([f"{c.name}={c.value}" for c in cookiejar])
        output_file.write_text(json.dumps({"cookies": cookie_string, "ssid": ssid, "user_agent": user_agent}, indent=4))
        self.close()

        return ssid, cookie_string

    def close(self):
        try:
            time.sleep(0.2)
            self.browser.close()
        except:
            pass
