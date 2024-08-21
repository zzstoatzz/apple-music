from datetime import datetime, timedelta
from typing import Any

import httpx
import jwt
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PrivateAttr


class AppleMusicClient(BaseModel):
    """A client for interacting with the Apple Music API.

    Attributes:
        private_key (str | bytes): The private key used to sign requests. Can be a string or bytes.
        key_id (str): The key ID used to sign requests.
        team_id (str): The team ID used to sign requests.
        proxies (dict[str, str] | None, optional): A dictionary of proxy URLs to use for requests. Defaults to None.
        max_retries (int, optional): The maximum number of retries for failed requests. Defaults to 10.
        timeout (float, optional): The timeout for requests in seconds. Defaults to 10.0.
        session_length (int, optional): The length of time in hours for which the client's token is valid. Defaults to 12.
        root (HttpUrl, optional): The root URL for the Apple Music API. Defaults to "https://api.music.apple.com/v1/".

        Examples:
            ```python
            from apple_music import AppleMusicClient

            async with AppleMusicClient(
                private_key="your_private_key",
                key_id="your_key_id",
                team_id="your_team_id"
            ) as client:
                song = await client.get_resource("song_id", "songs")
                print(song)
            ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    private_key: str | bytes
    key_id: str
    team_id: str
    proxies: dict[str, str] | None = None
    max_retries: int = 10
    timeout: float = 10.0
    session_length: int = 12
    root: HttpUrl = Field(default="https://api.music.apple.com/v1/")

    _client: httpx.AsyncClient | None = PrivateAttr(default=None)
    _token: str | None = PrivateAttr(default=None)
    _token_expires_at: datetime | None = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._client = httpx.AsyncClient(
            proxies=self.proxies,
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=self.max_retries),
        )

    async def __aenter__(self):
        return await self._client.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def _generate_token(self) -> str:
        self._token_expires_at = datetime.now() + timedelta(hours=self.session_length)
        headers = {"alg": "ES256", "kid": self.key_id}
        payload = {
            "iss": self.team_id,
            "iat": int(datetime.now().timestamp()),
            "exp": int(self._token_expires_at.timestamp()),
        }
        if isinstance(self.private_key, str):
            private_key = load_pem_private_key(self.private_key.encode(), password=None)
        else:
            private_key = self.private_key

        return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)

    def _get_token(self) -> str:
        if not self._token or datetime.now() >= self._token_expires_at:
            self._token = self._generate_token()
        return self._token

    async def _request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }
        if not url.startswith("http"):
            url = str(self.root) + url

        response = await self._client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_resource(
        self, resource_id: str, resource_type: str, storefront: str = "us", **kwargs
    ) -> dict[str, Any]:
        url = f"catalog/{storefront}/{resource_type}/{resource_id}"
        return await self._request("GET", url, **kwargs)

    async def get_resource_relationship(
        self,
        resource_id: str,
        resource_type: str,
        relationship: str,
        storefront: str = "us",
        **kwargs,
    ) -> dict[str, Any]:
        url = f"catalog/{storefront}/{resource_type}/{resource_id}/{relationship}"
        return await self._request("GET", url, **kwargs)

    async def get_multiple_resources(
        self,
        resource_ids: list[str],
        resource_type: str,
        storefront: str = "us",
        **kwargs,
    ) -> dict[str, Any]:
        url = f"catalog/{storefront}/{resource_type}"
        id_string = ",".join(resource_ids)
        return await self._request("GET", url, params={"ids": id_string, **kwargs})

    async def get_resource_by_filter(
        self,
        filter_type: str,
        filter_list: list[str],
        resource_type: str,
        resource_ids: list[str] | None = None,
        storefront: str = "us",
        **kwargs,
    ) -> dict[str, Any]:
        url = f"catalog/{storefront}/{resource_type}"
        params = {f"filter[{filter_type}]": ",".join(filter_list), **kwargs}
        if resource_ids:
            params["ids"] = ",".join(resource_ids)
        return await self._request("GET", url, params=params)
