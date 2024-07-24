"""Module for Quotex http refresh ssid resource."""

from quotexpy.http.navigator import Navigator


class Refresh(Navigator):
    """Class for Quotex refresh resource."""

    def __call__(self):
        try:
            response = self.send_request(
                method="GET",
                url=f"{self.https_base_url}/api/v1/cabinets/digest",
                headers={"User-Agent": self.api.user_agent, "Cookie": self.api.cookies},
            )

            if response.status_code == 200:
                response_json: dict = response.json()
                data: dict = response_json.get("data")
                if data and data.get("token"):
                    return data.get("token")
                raise KeyError("token not found in response data")
            raise ValueError("error refreshing ssid, maybe your client started without credentials?")
        except Exception as err:
            raise RuntimeError(f"unhandled error: {str(err)}") from err
