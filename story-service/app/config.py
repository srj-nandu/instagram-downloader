from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


def _resolve_path(raw_value: str | None, base_dir: Path, fallback: Path) -> Path:
    if not raw_value:
        return fallback.resolve()
    if Path(raw_value).is_absolute():
        return Path(raw_value).resolve()
    return (base_dir / raw_value).resolve()


@dataclass(frozen=True)
class Settings:
    downloads_dir: Path
    public_download_prefix: str
    instagram_username: str | None
    instagram_password: str | None
    instagram_session_file: Path | None
    cooldown_period: timedelta
    session_status_ttl_seconds: int


repo_root = Path(__file__).resolve().parents[2]
service_root = Path(__file__).resolve().parents[1]
load_dotenv(service_root / ".env")
downloads_root = _resolve_path(
    os.getenv("DOWNLOADS_DIR"),
    service_root,
    repo_root / "downloads",
)

session_file = os.getenv("INSTAGRAM_SESSION_FILE")
resolved_session_file = None
if session_file:
    resolved_session_file = _resolve_path(
        session_file,
        service_root,
        service_root / ".session",
    )

downloads_root.mkdir(parents=True, exist_ok=True)
if resolved_session_file:
    resolved_session_file.parent.mkdir(parents=True, exist_ok=True)

settings = Settings(
    downloads_dir=downloads_root,
    public_download_prefix=os.getenv("PUBLIC_DOWNLOAD_PREFIX", "/downloads"),
    instagram_username=os.getenv("INSTAGRAM_USERNAME") or None,
    instagram_password=os.getenv("INSTAGRAM_PASSWORD") or None,
    instagram_session_file=resolved_session_file,
    cooldown_period=timedelta(
        minutes=int(os.getenv("STORY_COOLDOWN_MINUTES", "30"))
    ),
    session_status_ttl_seconds=int(os.getenv("SESSION_STATUS_TTL_SECONDS", "60")),
)
