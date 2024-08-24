import webbrowser
from pathlib import Path
from typing import Iterable, Self

import spotipy
from prefect.blocks.abstract import CredentialsBlock
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from spotipy.oauth2 import SpotifyOAuth

from spotify2apple.types.filesystem import EnsuredPath


class SpotifyAuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SPOTIFY_", env_file=".env")

    client_id: str
    client_secret: SecretStr
    redirect_uri: str = "http://localhost:8888/callback"
    scopes: Iterable[str] = {
        "playlist-read-private",
        "user-library-read",
        "user-read-currently-playing",
        "user-read-playback-state",
    }

    @property
    def scope(self) -> str:
        return " ".join(self.scopes)


class SpotifyCredentials(CredentialsBlock):
    """Spotify credentials block for managing authentication with Spotify API"""

    settings: SpotifyAuthSettings = Field(default_factory=SpotifyAuthSettings)
    cache_path: EnsuredPath = Field(default_factory=lambda: Path(".spotify_cache"))

    def get_client(self: Self) -> spotipy.Spotify:
        """
        Returns a client for interacting with the Spotify API.
        Handles the OAuth flow if no valid token is present.

        Returns:
            A Spotify client instance.
        """

        auth_manager = SpotifyOAuth(
            client_id=self.settings.client_id,
            client_secret=self.settings.client_secret.get_secret_value(),
            redirect_uri=self.settings.redirect_uri,
            scope=self.settings.scope,
            cache_path=self.cache_path,
            open_browser=False,
        )

        if not auth_manager.get_cached_token():
            auth_url = auth_manager.get_authorize_url()
            self.logger.info(
                f"Please visit this URL to authorize the application: {auth_url}"
            )
            webbrowser.open(auth_url)

            # Use a local server to catch the redirect
            code = auth_manager.get_auth_response()
            auth_manager.get_access_token(code)

        return spotipy.Spotify(auth_manager=auth_manager)
