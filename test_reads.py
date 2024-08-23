import asyncio

from apple_music import AppleMusicClient
from apple_music.settings import settings


async def main(search_term: str = "love"):
    async with AppleMusicClient(
        private_key=settings.auth.private_key_path.read_text(),
        key_id=settings.auth.key_id,
        team_id=settings.auth.team_id,
    ) as client:
        print(f"Searching for {search_term!r}...")
        search_response = await client.search(search_term)

        print(f"Search results for '{search_term}':")

        for result in search_response.results.values():
            for song in result.data:
                print(f"Title: {song.attributes.name}")
                print(f"Artist: {song.attributes.artist_name}")
                print(f"Album: {song.attributes.album_name}")
                print(f"Genre: {song.attributes.genre_names}")
                print()


if __name__ == "__main__":
    asyncio.run(main())
