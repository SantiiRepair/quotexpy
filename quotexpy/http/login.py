from quotexpy.http.qxbroker import Browser


class Login(Browser):
    """Class for Quotex login resource."""

    url = ""
    ssid = None
    cookies = None
    base_url = "qxbroker.com"
    https_base_url = f"https://{base_url}"

    async def __call__(self, email: str, password: str, **kwargs):
        """
        Method to get Quotex API login http request.
        :param str username: The username of a Quotex server.
        :param str password: The password of a Quotex server.
        """

        self.email = email
        self.password = password
        self.headless = kwargs.get("headless", False)
        self.on_pin_code = kwargs.get("on_pin_code", None)

        self.ssid, self.cookies = self.get_cookies_and_ssid()
        return self.ssid, self.cookies
