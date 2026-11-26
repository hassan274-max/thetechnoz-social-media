#!/usr/bin/env python3
"""Safe queued Meta photo publishing for TheTechnoz Solutions.
No secrets in repository. Runs only when PUBLISHING_ENABLED=true and token exists.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "posts-queue.json"
LOG = ROOT / "publishing-log.json"
MANIFEST = ROOT / "assets-manifest.json"
API = "https://graph.facebook.com/v27.0"
PAGE_ID = "100499538904729"
IG_ID = "17841458273487103"
TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "").strip()
ENABLED = os.getenv("PUBLISHING_ENABLED", "").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

def utcnow():
    return datetime.now(timezone.utc)

def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def save(path, document):
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def graph(method, endpoint, params):
    data = dict(params)
    data["access_token"] = TOKEN
    url = f"{API}/{endpoint.lstrip('/')}"
    if method == "GET":
        url += "?" + urllib.parse.urlencode(data)
        request = urllib.request.Request(url, method="GET")
    else:
        request = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=45) as r:
            result = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        # Do not print arbitrary API response or sensitive request parameters.
        try:
            err = json.loads(body).get("error", {})
            raise RuntimeError(f"Graph API error {err.get('code')}: {err.get('message','unknown')[:250]}") from None
        except (ValueError, AttributeError):
            raise RuntimeError(f"Graph API HTTP {e.code}") from None
    if "error" in result:
        raise RuntimeError(f"Graph API returned error code {result['error'].get('code')}")
    return result

def ensure_manifest(asset, published_at):
    doc = load(MANIFEST, {"schema_version": 1, "assets": []})
    path = asset.get("path")
    if not path:
        return
    from datetime import timedelta
    expiry = published_at + timedelta(hours=72)
    for entry in doc.setdefault("assets", []):
        if entry.get("path") == path:
            return  # Never overwrite a preexisting record
    doc["assets"].append({
        "path": path,
        "status": "published",
        "published_at": published_at.isoformat().replace("+00:00", "Z"),
        "delete_after": expiry.isoformat().replace("+00:00", "Z")
    })
    save(MANIFEST, doc)

def main():
    queue = load(QUEUE, {"posts": []}).get("posts", [])
    log = load(LOG, {"posts": {}})
    now = utcnow()
    if not ENABLED:
        print("Publishing disabled. Set GitHub Actions variable PUBLISHING_ENABLED=true after setup.")
        return
    if not TOKEN and not DRY_RUN:
        print("META_PAGE_ACCESS_TOKEN secret missing. No posts attempted.")
        return
    for post in queue:
        ident = str(post.get("id", ""))
        scheduled = post.get("scheduled_at", "")
        if not ident or not scheduled:
            continue
        try:
            when = datetime.fromisoformat(scheduled.replace("Z","+00:00")).astimezone(timezone.utc)
        except ValueError:
            print(f"Skipping invalid scheduling on {ident}")
            continue
        if when > now:
            continue
        caption = post.get("caption", "").strip()
        img = post.get("image_url", "")
        targets = post.get("platforms", [])
        if not caption or not img.startswith("https://") or not set(targets).issubset({"facebook","instagram"}):
            print(f"Skipping invalid post {ident}")
            continue
        status = log.setdefault("posts", {}).setdefault(ident, {})
        for target in targets:
            if status.get(target, {}).get("status") == "published":
                continue
            if DRY_RUN:
                print(f"DRY RUN: {ident} -> {target}")
                continue
            try:
                if target == "facebook":
                    result = graph("POST", f"{PAGE_ID}/photos", {"url": img, "caption": caption, "published": "true"})
                    media_id = result.get("post_id") or result["id"]
                else:
                    container = graph("POST", f"{IG_ID}/media", {"image_url": img, "caption": caption})
                    container_id = container["id"]
                    for attempt in range(9):
                        check = graph("GET", container_id, {"fields": "status_code"})
                        if check.get("status_code") == "FINISHED":
                            break
                        if check.get("status_code") in ("ERROR", "EXPIRED"):
                            raise RuntimeError("Instagram container failed processing")
                        time.sleep(10)
                    else:
                        raise RuntimeError("Instagram media processing not yet finished; avoid immediate retry")
                    result = graph("POST", f"{IG_ID}/media_publish", {"creation_id": container_id})
                    media_id = result["id"]
                status[target] = {"status": "published", "id": media_id, "published_at": utcnow().isoformat()}
                save(LOG, log)
                print(f"Published {ident} to {target}, ID={media_id}")
            except Exception as exc:
                print(f"Could not publish {ident} to {target}: {exc}")
        # Only mark eligible for asset cleanup once every listed target is published.
        if targets and all(status.get(t, {}).get("status") == "published" for t in targets):
            ensure_manifest(post, utcnow())

if __name__ == "__main__":
    main()
