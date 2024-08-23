from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apple_music import AppleMusicClient
from apple_music.settings import settings

app = FastAPI()

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="spotify2apple/templates")


@asynccontextmanager
async def get_client() -> AsyncGenerator[AppleMusicClient, None]:
    """Utility to create and manage the AppleMusicClient context."""
    async with AppleMusicClient(
        private_key=settings.auth.private_key_path.read_text(),
        key_id=settings.auth.key_id,
        team_id=settings.auth.team_id,
    ) as client:
        yield client


async def get_developer_token() -> str:
    async with get_client() as client:
        return client._generate_token()


@router.get("/developer-token")
async def get_token(token: str = Depends(get_developer_token)):
    return {"token": token}


@router.get("/spotify-playlists")
async def get_spotify_playlists():
    # TODO: Implement the logic to fetch Spotify playlists
    raise HTTPException(status_code=501, detail="Not implemented")


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
