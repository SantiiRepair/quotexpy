"""Module for Quotex http logout resource."""

from quotexpy.http.navigator import Navigator


class Logout(Navigator):
    """Class for Quotex logout resource."""

    def __call__(self):
        response = self.send_request(
            method="GET",
            url=f"{self.https_base_url}/logout",
            headers={"User-Agent": self.api.user_agent, "Cookie": self.api.cookies},
        )

        return response
