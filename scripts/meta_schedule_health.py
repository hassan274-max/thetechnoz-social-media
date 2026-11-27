#!/usr/bin/env python3
"""Fail closed if today's due Meta image or Reel is missing or partly unpublished.

Use after the publisher attempts; never publishes or modifies credentials.
Only checks today's target slots, not historical posts.
"""
import json
from datetime import datetime,timezone,timedelta,time
from pathlib import Path
PKT=timezone(timedelta(hours=5))
today=datetime.now(PKT).date()
now=datetime.now(PKT)
root=Path(__file__).resolve().parents[1]
queue=json.loads((root/"posts-queue.json").read_text(encoding="utf-8"))
log=json.loads((root/"publishing-log.json").read_text(encoding="utf-8")).get("posts",{})
ids={p.get("id"):p for p in queue.get("posts",[])}
failed=[]
for kind,hour in (("image",11),("reel",19)):
    # Allow the primary scheduler and API publishing a short grace period.
    due=datetime.combine(today,time(hour,2),PKT)
    if now<due:
        continue
    ident=f"{today.isoformat()}-{kind}"
    post=ids.get(ident)
    if not post:
        failed.append(f"{ident}: missing from prepared queue")
        continue
    for platform in ("facebook","instagram"):
        if platform not in post.get("platforms",[]):
            failed.append(f"{ident}: {platform} is not an enabled target")
        elif log.get(ident,{}).get(platform,{}).get("status")!="published":
            failed.append(f"{ident}: {platform} has no confirmed published ID")
if failed:
    for line in failed: print("SCHEDULE_MISSED: "+line)
    raise SystemExit(1)
print("Meta schedule health OK: every due platform slot confirmed published, or not yet due.")
