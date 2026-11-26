#!/usr/bin/env python3
"""One-time LOCAL YouTube channel authorization.
Do not run with client secrets in a public GitHub Actions log.
Run on your own computer; never commit credentials or token files.
"""
import argparse
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--client", default="client_secret.json",
                   help="Path to downloaded Google OAuth Desktop Client JSON")
    p.add_argument("--output", default="youtube_token.json")
    args = p.parse_args()
    client = Path(args.client)
    if not client.is_file():
        p.error(f"Missing OAuth client JSON: {client}")
    flow = InstalledAppFlow.from_client_secrets_file(str(client), SCOPES)
    creds = flow.run_local_server(host="localhost", port=0,
                                  access_type="offline", prompt="consent")
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    channels = yt.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not channels:
        raise RuntimeError("No YouTube channel accessible. Choose the right Google account/channel and try again.")
    print("Authorized channels (verify before publishing):")
    for channel in channels:
        print(f"  Channel title: {channel['snippet']['title']}; Channel ID: {channel['id']}")
    Path(args.output).write_text(creds.to_json(), encoding="utf-8")
    print(f"Local private token saved to {args.output}; NEVER commit, paste, or send this file.")

if __name__ == "__main__":
    main()
