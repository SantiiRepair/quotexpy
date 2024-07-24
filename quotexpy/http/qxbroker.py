import os
import time
import pickle
import typing
import psutil
import random
import requests
from pathlib import Path
import undetected_chromedriver as uc
from quotexpy.http.user_agents import agents
from quotexpy.utils import sessions_file_path
from quotexpy.exceptions import QuotexAuthError
from selenium.common.exceptions import JavascriptException


class Browser(object):
    email = None
    password = None
    on_pin_code = None
    headless = None

    base_url = "qxbroker.com"
    https_base_url = f"https://{base_url}"

    def __init__(self, api):
        self.api = api

        user_agent_list = agents.split("\n")
        self.user_agent = (
            self.api.user_agent if self.api.user_agent else user_agent_list[random.randint(0, len(user_agent_list) - 1)]
        )

    def get_ssid_and_cookies(self) -> typing.Tuple[str, str]:
        try:
            options = uc.ChromeOptions()
            options.add_argument(f"--user-agent={self.user_agent}")
            self.browser = uc.Chrome(options=options, headless=self.headless, use_subprocess=False)

            self.browser.get(f"{self.https_base_url}/en/sign-in")

            rb = self.browser.execute_script('return document.querySelector(".modal-sign__not-avalible") !== null;')
            if rb:
                raise ConnectionError("quotex is currently not available in your region")

            if "trade" not in self.browser.current_url:
                try:
                    self.browser.execute_script(
                        'document.getElementsByName("email")[1].value = arguments[0];', self.email
                    )
                    self.browser.execute_script(
                        'document.getElementsByName("password")[1].value = arguments[0];', self.password
                    )
                    self.browser.execute_script(
                        """document.evaluate("//div[@id='tab-1']/form", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.submit();"""
                    )
                except JavascriptException as exc:
                    raise ConnectionRefusedError("blocked by cloudflare, deactivate headless") from exc

            code_input = self.browser.execute_script('return document.querySelector("[name=code]") !== null;')
            if code_input:
                if self.on_pin_code is None:
                    raise ValueError("account has 2fa enabled but was not given a hook to manage it")
                code = self.on_pin_code()
                self.browser.execute_script('document.querySelector("[name=code]").value = arguments[0];', code)
                btn = self.browser.find_element(uc.By.XPATH, "//button[@type='submit']")
                btn.click()

                time.sleep(random.randint(2, 4))
                bc = self.browser.execute_script('return document.querySelector(".hint.hint--danger") !== null;')
                if bc:
                    raise QuotexAuthError("the pin code is incorrect")

            wsd: typing.Union[dict, None] = self.browser.execute_script("return window.settings;")
            if wsd is None or "token" not in wsd:
                raise QuotexAuthError("incorrect username or password")

            cookies = self.browser.get_cookies()
            self.api.user_agent = self.browser.execute_script("return navigator.userAgent;")

            ssid = wsd.get("token")
            cookiejar = requests.utils.cookiejar_from_dict({c["name"]: c["value"] for c in cookies})
            self.api.cookies = "; ".join([f"{c.name}={c.value}" for c in cookiejar])
            output_file = Path(sessions_file_path)
            output_file.parent.mkdir(exist_ok=True, parents=True)

            data = {}
            if output_file.is_file():
                with output_file.open("rb") as file:
                    data = pickle.load(file)

            data[self.email] = [{"cookies": self.api.cookies, "ssid": ssid, "user_agent": self.api.user_agent}]
            with output_file.open("wb") as file:
                pickle.dump(data, file)

            return ssid, self.api.cookies
        except TypeError as exc:
            raise SystemError("Chrome is not installed, did you forget?") from exc
        finally:
            self.close()

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
