import asyncio

from apple_music import get_client


async def main(search_term: str = "love"):
    async with get_client() as client:
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
