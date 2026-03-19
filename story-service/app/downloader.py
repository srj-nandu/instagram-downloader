from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import instaloader

from app.config import Settings

MEDIA_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".webp"}
SHORTCODE_PATTERN = re.compile(
    r"instagram\.com/(?:p|reel|tv)/(?P<shortcode>[\w-]+)/?",
    re.IGNORECASE,
)
PROFILE_PATTERN = re.compile(
    r"instagram\.com/(?P<username>[A-Za-z0-9._]+)/?(?:\?.*)?$",
    re.IGNORECASE,
)


class DownloadError(Exception):
    pass


class InvalidInstagramUrlError(DownloadError):
    pass


class InvalidInstagramProfileUrlError(DownloadError):
    pass


class RateLimitedError(DownloadError):
    pass


class AuthConfigurationError(DownloadError):
    pass


class NoStoriesAvailableError(DownloadError):
    pass


class InstagramDownloader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._cooldown_until: datetime | None = None
        self._session_status_cache: dict[str, object] | None = None
        self._session_status_cached_at: datetime | None = None

    @property
    def story_login_configured(self) -> bool:
        has_session = bool(
            self.settings.instagram_username and self.settings.instagram_session_file
        )
        has_credentials = bool(
            self.settings.instagram_username and self.settings.instagram_password
        )
        return has_session or has_credentials

    def get_capabilities(self) -> dict[str, object]:
        return {
            "storiesRequireLogin": True,
            "storyLoginConfigured": self.story_login_configured,
            "cooldownUntil": self._cooldown_until_iso(),
            "cooldownActive": self._cooldown_active,
        }

    def get_session_status(self, force_refresh: bool = False) -> dict[str, object]:
        if not force_refresh and self._session_cache_valid:
            return self._session_status_cache or self._build_session_status()

        if self._cooldown_active:
            status = self._build_session_status(
                session_healthy=False,
                detail=(
                    "Instagram recently rate-limited this session. Wait for the "
                    "cooldown before checking again."
                ),
            )
            self._cache_session_status(status)
            return status

        if not self.story_login_configured:
            status = self._build_session_status(
                session_healthy=False,
                detail="Story login is not configured.",
            )
            self._cache_session_status(status)
            return status

        loader = self._create_loader()

        try:
            self._authenticate(loader)
            authenticated_username = loader.test_login()
            if not authenticated_username:
                raise AuthConfigurationError(
                    "Instagram session could not be verified. Recreate the session."
                )
            status = self._build_session_status(
                session_healthy=True,
                authenticated_username=authenticated_username,
                detail=f"Authenticated as @{authenticated_username}.",
            )
        except Exception as exc:
            if self._is_rate_limited_exception(exc):
                self._mark_cooldown()
            status = self._build_session_status(
                session_healthy=False,
                detail=self._session_error_message(exc),
            )

        self._cache_session_status(status)
        return status

    def download_post(self, url: str) -> dict:
        shortcode = self._extract_shortcode(url)
        target = self._make_target("post", shortcode)
        loader = self._create_loader()

        try:
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target=target)
        except Exception as exc:
            self._raise_download_error(exc, "download post media")

        files = self._collect_media_files(target)
        return {
            "kind": "post",
            "folder": target,
            "message": f"Downloaded {len(files)} file(s) from post {shortcode}.",
            "files": files,
        }

    def download_stories(self, profile_url: str) -> dict:
        normalized_username = self._extract_profile_username(profile_url)
        return self._download_stories_for_username(normalized_username, "stories")

    def download_my_stories(self) -> dict:
        loader = self._create_loader()
        self._ensure_story_access(loader)
        try:
            authenticated_username = loader.test_login()
        except Exception as exc:
            self._raise_download_error(exc, "verify the authenticated session")

        if not authenticated_username:
            raise AuthConfigurationError(
                "Instagram session could not be verified. Recreate the session."
            )

        return self._download_stories_for_username(
            authenticated_username,
            "my-stories",
        )

    def _download_stories_for_username(self, username: str, target_kind: str) -> dict:
        loader = self._create_loader()
        self._ensure_story_access(loader)
        target = self._make_target(target_kind, username)

        try:
            profile = instaloader.Profile.from_username(loader.context, username)
            stories = list(loader.get_stories(userids=[profile.userid]))
            items = [item for story in stories for item in story.get_items()]
        except Exception as exc:
            self._raise_download_error(exc, "fetch stories")

        if not items:
            raise NoStoriesAvailableError(f"No active stories were found for @{username}.")

        try:
            for item in items:
                loader.download_storyitem(item, target=target)
        except Exception as exc:
            self._raise_download_error(exc, "download story media")

        files = self._collect_media_files(target)
        return {
            "kind": "stories",
            "folder": target,
            "message": f"Downloaded {len(files)} story file(s) for @{username}.",
            "files": files,
        }

    def _create_loader(self) -> instaloader.Instaloader:
        return instaloader.Instaloader(
            dirname_pattern=str(self.settings.downloads_dir / "{target}"),
            filename_pattern="{date_utc}_UTC",
            download_comments=False,
            download_geotags=False,
            save_metadata=False,
            compress_json=False,
            download_video_thumbnails=False,
            max_connection_attempts=1,
            fatal_status_codes=[429],
            quiet=True,
        )

    def _authenticate(self, loader: instaloader.Instaloader) -> None:
        username = self.settings.instagram_username
        password = self.settings.instagram_password
        session_file = self.settings.instagram_session_file

        if username and session_file and session_file.exists():
            try:
                loader.load_session_from_file(username, str(session_file))
                return
            except Exception:
                if not password:
                    raise

        if username and password:
            loader.login(username, password)
            if session_file:
                loader.save_session_to_file(str(session_file))
            return

        raise AuthConfigurationError(
            "Instagram story access is not configured correctly."
        )

    def _ensure_story_access(self, loader: instaloader.Instaloader) -> None:
        self._ensure_not_cooling_down()
        if not self.story_login_configured:
            raise AuthConfigurationError(
                "Story downloads require INSTAGRAM_USERNAME with either "
                "INSTAGRAM_PASSWORD or INSTAGRAM_SESSION_FILE."
            )
        try:
            self._authenticate(loader)
        except AuthConfigurationError:
            raise
        except Exception as exc:
            self._raise_download_error(exc, "authenticate the Instagram session")

    def _extract_shortcode(self, url: str) -> str:
        match = SHORTCODE_PATTERN.search(url.strip())
        if not match:
            raise InvalidInstagramUrlError(
                "Use a full Instagram post, reel, or TV URL."
            )
        return match.group("shortcode")

    def _extract_profile_username(self, profile_url: str) -> str:
        match = PROFILE_PATTERN.search(profile_url.strip().rstrip("/"))
        if not match:
            raise InvalidInstagramProfileUrlError(
                "Use a full Instagram profile URL."
            )

        username = match.group("username").strip().lstrip("@")
        if username.lower() in {"p", "reel", "reels", "tv", "stories"}:
            raise InvalidInstagramProfileUrlError(
                "Use a full Instagram profile URL."
            )

        return username

    def _make_target(self, kind: str, slug: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower()
        return f"{kind}-{safe_slug}-{timestamp}-{uuid4().hex[:8]}"

    def _raise_download_error(self, exc: Exception, action: str) -> None:
        if self._is_rate_limited_exception(exc):
            self._mark_cooldown()
            self._session_status_cache = None
            raise RateLimitedError(
                "Instagram rate-limited this request. Wait for the cooldown and "
                "try again. Avoid repeated story requests or using the Instagram "
                "app in parallel."
            ) from exc

        raise DownloadError(f"Unable to {action}: {exc}") from exc

    @property
    def _cooldown_active(self) -> bool:
        return bool(self._cooldown_until and self._cooldown_until > self._utcnow())

    @property
    def _session_cache_valid(self) -> bool:
        if not self._session_status_cache or not self._session_status_cached_at:
            return False
        age = self._utcnow() - self._session_status_cached_at
        return age.total_seconds() < self.settings.session_status_ttl_seconds

    def _mark_cooldown(self) -> None:
        self._cooldown_until = self._utcnow() + self.settings.cooldown_period

    def _ensure_not_cooling_down(self) -> None:
        if not self._cooldown_active:
            return
        cooldown_text = self._cooldown_until.strftime("%Y-%m-%d %H:%M:%S UTC")
        raise RateLimitedError(
            f"Instagram is in cooldown for this session until {cooldown_text}."
        )

    def _cache_session_status(self, status: dict[str, object]) -> None:
        self._session_status_cache = status
        self._session_status_cached_at = self._utcnow()

    def _build_session_status(
        self,
        *,
        session_healthy: bool | None = None,
        authenticated_username: str | None = None,
        detail: str | None = None,
    ) -> dict[str, object]:
        session_file_present = bool(
            self.settings.instagram_session_file
            and self.settings.instagram_session_file.exists()
        )
        return {
            "storyLoginConfigured": self.story_login_configured,
            "sessionHealthy": session_healthy,
            "authenticatedUsername": authenticated_username,
            "sessionFilePresent": session_file_present,
            "cooldownUntil": self._cooldown_until_iso(),
            "cooldownActive": self._cooldown_active,
            "detail": detail,
        }

    def _cooldown_until_iso(self) -> str | None:
        if not self._cooldown_active:
            self._cooldown_until = None
            return None
        return self._cooldown_until.isoformat()

    def _session_error_message(self, exc: Exception) -> str:
        if self._is_rate_limited_exception(exc):
            return (
                "Instagram rate-limited this session. Wait for the cooldown before "
                "trying again."
            )
        return f"Session check failed: {exc}"

    def _is_rate_limited_exception(self, exc: Exception) -> bool:
        message = str(exc)
        return "429" in message or "Too Many Requests" in message

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    def _collect_media_files(self, target: str) -> list[dict]:
        target_dir = self.settings.downloads_dir / target
        files = []

        for path in sorted(target_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in MEDIA_EXTENSIONS:
                continue

            relative_path = path.relative_to(self.settings.downloads_dir).as_posix()
            files.append(
                {
                    "name": path.name,
                    "mediaType": self._media_type(path),
                    "publicPath": (
                        f"{self.settings.public_download_prefix}/{relative_path}"
                    ),
                    "sizeBytes": path.stat().st_size,
                }
            )

        if not files:
            raise DownloadError("No downloadable media files were produced.")

        return files

    def _media_type(self, path: Path) -> str:
        if path.suffix.lower() == ".mp4":
            return "video"
        return "image"
