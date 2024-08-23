import datetime
from contextlib import asynccontextmanager
from typing import Any

import logfire
import marvin
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apple_music import AppleMusicClient
from apple_music.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager to ensure the app is closed properly."""
    with logfire.span("Running app", start_time=datetime.datetime.now(datetime.UTC)):
        yield
    logfire.info("App closed")


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="spotify2apple/templates")


logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
logfire.instrument_fastapi(app)


async def get_developer_token() -> str:
    async with AppleMusicClient(
        private_key=settings.auth.private_key_path.read_text(),
        key_id=settings.auth.key_id,
        team_id=settings.auth.team_id,
    ) as client:
        return client._generate_token()


@router.get("/developer-token")
async def get_token(token: str = Depends(get_developer_token)):
    return {"token": token}


@router.get("/welcome-message")
async def welcome_message() -> str:
    message = (
        await marvin.generate_async(
            str,
            n=1,
            instructions="cheeky few word welcome to app that migrates spotify playlists to apple music",
        )
    )[0]
    logfire.info(f"Generated welcome message: {message}")
    return message


@router.get("/spotify-playlists")
async def get_spotify_playlists() -> list[dict[str, Any]]:
    """Get a list of Spotify playlists for the user."""
    return await marvin.generate_async(
        dict,
        n=5,
        instructions="list of playlists for user -- eclectic mix of genres",
    )


@router.get("/apple-playlists")
async def get_apple_playlists() -> list[dict[str, Any]]:
    """Get a list of Apple Music playlists for the user."""
    return [{"id": "123", "name": "Test Playlist"}]


@router.post("/migrate-playlists")
async def migrate_playlists(user_token: str, playlists: list[str]):
    # TODO: Implement the logic to migrate playlists to Apple Music
    raise HTTPException(status_code=501, detail="Not implemented")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)
