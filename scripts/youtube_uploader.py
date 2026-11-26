#!/usr/bin/env python3
"""TheTechnoz YouTube uploader: validate OAuth/channel first, optionally upload a Short.

Credentials come ONLY from GitHub Actions secrets, never repository files.
No upload unless explicit --upload, --file and --expected-channel-id are supplied.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[1]
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def credentials_from_secrets():
    raw_token = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    raw_client = os.environ.get("YOUTUBE_CLIENT_SECRET_JSON", "").strip()
    if not raw_token or not raw_client:
        raise RuntimeError("Missing YOUTUBE_TOKEN_JSON or YOUTUBE_CLIENT_SECRET_JSON Actions secret")
    token = json.loads(raw_token)
    client_doc = json.loads(raw_client)
    client = client_doc.get("installed") or client_doc.get("web")
    if not isinstance(client, dict):
        raise RuntimeError("OAuth client JSON must contain 'installed' or 'web' credentials")
    if client.get("client_id") != token.get("client_id"):
        raise RuntimeError("OAuth client_id does not match the saved token")
    if not token.get("refresh_token"):
        raise RuntimeError("Saved OAuth token has no refresh_token; authorize offline access again locally")

    # The user-authorized token JSON already contains the credentials needed
    # to refresh. Cross-validate it with the separately supplied OAuth client.
    info = dict(token)
    info["client_secret"] = client["client_secret"]
    if not info.get("scopes"):
        info["scopes"] = SCOPES
    creds = Credentials.from_authorized_user_info(info, scopes=SCOPES)
    if not creds.valid:
        creds.refresh(Request())
    if not creds.valid:
        raise RuntimeError("OAuth token refresh failed")
    return creds


def safe_relative_file(path_text):
    candidate = (ROOT / path_text).resolve()
    if not candidate.is_relative_to(ROOT):
        raise RuntimeError("Upload file must be inside repository")
    if candidate.suffix.lower() != ".mp4" or not candidate.is_file():
        raise RuntimeError("MP4 file not found in repository: " + path_text)
    if candidate.stat().st_size < 1024:
        raise RuntimeError("Video file looks empty")
    return candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload", action="store_true",
                        help="Explicitly upload the supplied MP4; defaults to authorization test only")
    parser.add_argument("--file", default="")
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--expected-channel-id", default="",
                        help="Require precise channel identity before any upload")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private",
                        help="Default private; public only on explicit request")
    args = parser.parse_args()

    creds = credentials_from_secrets()
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    result = yt.channels().list(part="snippet", mine=True).execute()
    channels = result.get("items", [])
    if len(channels) != 1:
        raise RuntimeError(f"Expected exactly one authorized channel, got {len(channels)}")
    actual_id = channels[0]["id"]
    actual_name = channels[0]["snippet"].get("title", "")
    print("AUTHORIZED CHANNEL:", actual_name)
    print("CHANNEL ID:", actual_id)
    if args.expected_channel_id and args.expected_channel_id != actual_id:
        raise RuntimeError("Expected YouTube channel ID does not match authorized channel")
    if not args.upload:
        print("SUCCESS: OAuth refresh and YouTube channel lookup succeeded. No upload attempted.")
        return
    if not args.expected_channel_id:
        raise RuntimeError("Uploads require an expected YouTube channel ID")
    if not args.title.strip():
        raise RuntimeError("Video title required")
    file = safe_relative_file(args.file)
    print(f"Uploading {file.relative_to(ROOT)} as {args.privacy} to {actual_name}")
    body = {
        "snippet": {
            "title": args.title[:100],
            "description": args.description[:4900],
            "categoryId": "28",
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    request = yt.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(file), mimetype="video/mp4",
                                  chunksize=1024 * 1024, resumable=True),
    )
    response = None
    # Do not automatically retry ambiguous complete requests: prevent duplicates.
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError("Upload did not return a video ID; check YouTube Studio")
    print("UPLOAD SUCCESS:", "https://www.youtube.com/watch?v=" + video_id)
    print("PRIVACY:", args.privacy)
    print("Video uploaded; verify playback and status in YouTube Studio before setting public.")


if __name__ == "__main__":
    try:
        main()
    except HttpError as exc:
        print(f"YouTube API HTTP error: {exc.resp.status} (details omitted)", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        # Avoid printing any credential values from Google exceptions.
        print(f"ERROR: {type(exc).__name__}: {str(exc)[:220]}", file=sys.stderr)
        sys.exit(1)
