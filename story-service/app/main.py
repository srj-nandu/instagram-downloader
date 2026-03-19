from fastapi import FastAPI, HTTPException

from app.config import settings
from app.downloader import (
    AuthConfigurationError,
    DownloadError,
    InstagramDownloader,
    InvalidInstagramProfileUrlError,
    InvalidInstagramUrlError,
    NoStoriesAvailableError,
    RateLimitedError,
)
from app.models import DownloadPostRequest, DownloadStoriesRequest

app = FastAPI(title="Story Service")
downloader = InstagramDownloader(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "story-service", "status": "ok"}


@app.get("/capabilities")
def capabilities() -> dict[str, object]:
    return downloader.get_capabilities()


@app.get("/session")
def session_status(force_refresh: bool = False) -> dict[str, object]:
    return downloader.get_session_status(force_refresh=force_refresh)


@app.post("/downloads/post")
def download_post_media(payload: DownloadPostRequest) -> dict:
    try:
        return downloader.download_post(payload.url)
    except InvalidInstagramUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RateLimitedError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except DownloadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/downloads/stories")
def download_story_media(payload: DownloadStoriesRequest) -> dict:
    try:
        return downloader.download_stories(payload.profile_url)
    except InvalidInstagramProfileUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AuthConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NoStoriesAvailableError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RateLimitedError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except DownloadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/downloads/stories/me")
def download_my_story_media() -> dict:
    try:
        return downloader.download_my_stories()
    except AuthConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NoStoriesAvailableError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RateLimitedError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except DownloadError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
