from __future__ import annotations

import getpass
import sys

import instaloader
from dotenv import load_dotenv

from app.config import service_root, settings


def main() -> int:
    load_dotenv(service_root / ".env")

    username = settings.instagram_username or input("Instagram username: ").strip()
    password = settings.instagram_password or getpass.getpass("Instagram password: ")
    session_file = settings.instagram_session_file or (service_root / ".session")

    if not username or not password:
        print("Username and password are required to create a session file.")
        return 1

    loader = instaloader.Instaloader(
        quiet=False,
        download_comments=False,
        download_geotags=False,
        save_metadata=False,
        compress_json=False,
        download_video_thumbnails=False,
        max_connection_attempts=1,
    )

    try:
        loader.login(username, password)
    except instaloader.TwoFactorAuthRequiredException:
        code = input("Instagram 2FA code: ").strip()
        if not code:
            print("2FA code is required.")
            return 1
        loader.two_factor_login(code)
    except Exception as exc:
        print(f"Login failed: {exc}")
        return 1

    session_file.parent.mkdir(parents=True, exist_ok=True)
    loader.save_session_to_file(str(session_file))
    print(f"Saved session to {session_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
