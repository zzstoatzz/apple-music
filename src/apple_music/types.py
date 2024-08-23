from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Artwork(BaseModel):
    model_config = ConfigDict(extra="allow")
    width: int = Field(..., description="The width of the artwork image in pixels.")
    height: int = Field(..., description="The height of the artwork image in pixels.")
    url: HttpUrl = Field(..., description="The URL of the artwork image.")


class SongAttributes(BaseModel):
    model_config = ConfigDict(extra="allow")
    album_name: str = Field(
        ..., alias="albumName", description="The name of the album."
    )
    genre_names: list[str] = Field(
        ...,
        alias="genreNames",
        description="List of genre names associated with the song.",
    )
    name: str = Field(..., description="The name of the song.")
    artist_name: str = Field(
        ...,
        alias="artistName",
        description="The name of the artist who performed the song.",
    )


class SongData(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(..., description="The unique identifier for the song.")
    type: str = Field(
        ..., description="The type of the resource, which is 'songs' in this context."
    )
    href: str = Field(
        ..., description="The resource URL for the song in the Apple Music catalog."
    )
    attributes: SongAttributes = Field(
        ..., description="Attributes associated with the song."
    )


class SongsResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    href: str | None = Field(
        None, description="The URL for the next set of results, if available."
    )
    next: str | None = Field(
        None, description="The URL for the next page of results, if available."
    )
    data: list[SongData] = Field(
        ..., description="List of songs returned in the search results."
    )


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    results: dict[str, SongsResult] = Field(
        ..., description="The search results grouped by resource type."
    )
    meta: dict | None = Field(None, description="Metadata about the search results.")
