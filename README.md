# apple-music

this is an opinionated rewrite of [`apple-music-python`](https://github.com/mpalazzolo/apple-music-python/tree/master), shoutout to the original author for the inspiration.

## getting started

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
see `tests/test_client.py` for more examples

## TODO
- write functionality (i.e. create)