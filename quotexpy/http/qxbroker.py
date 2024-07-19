import os
import re
import json
import pickle
import typing
import random
import psutil
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from quotexpy.http.user_agents import agents
from quotexpy.utils import sessions_file_path
from quotexpy.exceptions import QuotexAuthError
from selenium.common.exceptions import JavascriptException


class Browser(object):
    email = None
    password = None
    on_ping_code = None
    headless = None

    base_url = "qxbroker.com"
    https_base_url = f"https://{base_url}"

    def __init__(self, api):
        self.api = api

        user_agent_list = agents.split("\n")
        self.user_agent = (
            self.api.user_agent if self.api.user_agent else user_agent_list[random.randint(0, len(user_agent_list) - 1)]
        )

    def get_cookies_and_ssid(self) -> typing.Tuple[str, str]:
        try:
            options = uc.ChromeOptions()
            options.add_argument(f"--user-agent={self.user_agent}")
            self.browser = uc.Chrome(options=options, headless=self.headless, use_subprocess=False)
        except TypeError as exc:
            raise SystemError("Chrome is not installed, did you forget?") from exc
        self.browser.get(f"{self.https_base_url}/en/sign-in")

        if "trade" not in self.browser.current_url:
            try:
                self.browser.execute_script('document.getElementsByName("email")[1].value = arguments[0];', self.email)
                self.browser.execute_script(
                    'document.getElementsByName("password")[1].value = arguments[0];', self.password
                )
                self.browser.execute_script(
                    """document.evaluate("//div[@id='tab-1']/form", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.submit();"""
                )
            except JavascriptException as exc:
                raise ConnectionRefusedError("blocked by cloudflare, deactivate headless") from exc

        try:
            code_input = self.browser.find_element(uc.By.NAME, "code")
            if code_input.is_displayed():
                code = self.on_ping_code()
                code_input.send_keys(code)
                btn = self.browser.find_element(uc.By.XPATH, "//button[@type='submit']")
                btn.click()
        except:
            pass

        cookies = self.browser.get_cookies()
        self.api.cookies = cookies
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        user_agent = self.browser.execute_script("return navigator.userAgent;")
        self.api.user_agent = user_agent

        try:
            script: str = soup.find_all("script", {"type": "text/javascript"})[1].get_text()
        except Exception as exc:
            raise QuotexAuthError("incorrect username or password") from exc
        finally:
            self.close()

        match = re.sub("window.settings = ", "", script.strip().replace(";", ""))

        dx: dict = json.loads(match)
        ssid = dx.get("token")

        cookiejar = requests.utils.cookiejar_from_dict({c["name"]: c["value"] for c in cookies})
        cookie_string = "; ".join([f"{c.name}={c.value}" for c in cookiejar])
        output_file = Path(sessions_file_path)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        data = {}
        if output_file.is_file():
            with output_file.open("rb") as file:
                data = pickle.load(file)

        data[self.email] = [{"cookies": cookie_string, "ssid": ssid, "user_agent": user_agent}]
        with output_file.open("wb") as file:
            pickle.dump(data, file)

        return ssid, cookie_string

    def close(self):
        """
        Safely terminates all running instances of the Google Chrome web browser.
        """

        if os.name == "nt":
            process_name = "chrome.exe"
        elif os.uname().sysname == "Darwin":
            process_name = "Google Chrome"
        else:
            process_name = "chrome"

        for proc in psutil.process_iter(["name", "exe"]):
            try:
                if process_name in (proc.info["name"], str(proc.info["exe"])):
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
