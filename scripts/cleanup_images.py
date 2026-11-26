#!/usr/bin/env python3
"""Remove explicitly registered, successfully published social assets after retention.

Only files listed in assets-manifest.json with status=published and delete_after
in the past can be removed. No directory scanning or automatic guesswork.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets-manifest.json"

def parse_utc(raw):
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)

def main():
    if not MANIFEST.exists():
        print("No manifest; nothing to clean")
        return
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = document.get("assets", [])
    now = datetime.now(timezone.utc)
    removed = []
    for item in entries:
        if item.get("status") != "published":
            continue
        path = item.get("path", "")
        published_at = item.get("published_at")
        delete_after = item.get("delete_after")
        if not path or not published_at or not delete_after:
            continue
        try:
            rel = Path(path)
            if (rel.is_absolute() or ".." in rel.parts or rel.suffix.lower() not in
                    {".png", ".jpg", ".jpeg", ".webp", ".mp4"}):
                print(f"Skipping unsafe path: {path}")
                continue
            target = (ROOT / rel).resolve()
            if not target.is_relative_to(ROOT):
                continue
            pub, expiry = parse_utc(published_at), parse_utc(delete_after)
            if expiry < pub or (expiry - pub).total_seconds() < 72 * 3600:
                print(f"Skipping insufficient retention: {path}")
                continue
            if now < expiry:
                continue
            if target.is_file():
                target.unlink()
                removed.append(path)
                print(f"Removed expired published asset: {path}")
            item["status"] = "cleaned"
            item["cleaned_at"] = now.isoformat()
        except (ValueError, TypeError, OSError) as exc:
            print(f"Skipped {path}: {exc}")
    if any(e.get("status") == "cleaned" and e.get("cleaned_at") for e in entries):
        MANIFEST.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Finished: {len(removed)} image/video files deleted")

if __name__ == "__main__":
    main()
