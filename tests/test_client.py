from datetime import datetime, timedelta

import pytest
import respx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import Response

from apple_music import AppleMusicClient


@pytest.fixture(scope="module")
def private_key_bytes() -> bytes:
    key = ec.generate_private_key(ec.SECP256R1())
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture(params=["bytes", "str"])  # run suite both with bytes and str
def private_key(request, private_key_bytes: bytes) -> str | bytes:
    if request.param == "bytes":
        return private_key_bytes
    else:
        return private_key_bytes.decode()


@pytest.fixture
def client(private_key: str | bytes) -> AppleMusicClient:
    return AppleMusicClient(
        private_key=private_key, key_id="test_key_id", team_id="test_team_id"
    )


def test_token_generation(client):
    token = client._get_token()
    assert token and len(token.split(".")) == 3, "Token should be a valid JWT"


async def test_get_resource(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs/123").mock(
            return_value=Response(200, json={"data": [{"id": "123", "type": "songs"}]})
        )
        result = await client.get_resource("123", "songs")
        assert result == {"data": [{"id": "123", "type": "songs"}]}


async def test_get_resource_relationship(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs/123/albums").mock(
            return_value=Response(200, json={"data": [{"id": "456", "type": "albums"}]})
        )
        result = await client.get_resource_relationship("123", "songs", "albums")
        assert result == {"data": [{"id": "456", "type": "albums"}]}


async def test_get_multiple_resources(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs").mock(
            return_value=Response(
                200,
                json={
                    "data": [
                        {"id": "123", "type": "songs"},
                        {"id": "456", "type": "songs"},
                    ]
                },
            )
        )
        result = await client.get_multiple_resources(["123", "456"], "songs")
        assert result == {
            "data": [{"id": "123", "type": "songs"}, {"id": "456", "type": "songs"}]
        }


async def test_get_resource_by_filter(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs").mock(
            return_value=Response(200, json={"data": [{"id": "123", "type": "songs"}]})
        )
        result = await client.get_resource_by_filter(
            "artistName", ["Test Artist"], "songs"
        )
        assert result == {"data": [{"id": "123", "type": "songs"}]}


async def test_error_handling(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs/999").mock(
            return_value=Response(
                404, json={"errors": [{"status": "404", "title": "Not Found"}]}
            )
        )
        with pytest.raises(
            Exception
        ):  # You might want to be more specific about the exception type
            await client.get_resource("999", "songs")


async def test_token_refresh(client):
    with respx.mock:
        respx.get("https://api.music.apple.com/v1/catalog/us/songs/123").mock(
            return_value=Response(200, json={"data": [{"id": "123", "type": "songs"}]})
        )
        client._token_expires_at = datetime.now() - timedelta(hours=1)
        old_token = client._token
        await client.get_resource("123", "songs")
        assert client._token != old_token
        assert client._token_expires_at > datetime.now()
