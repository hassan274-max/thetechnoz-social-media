#!/usr/bin/env python3
"""Prepare original animated educational Reels for Facebook and Instagram.

Uses the user-approved YouTube motion-graphics engine as a shared video
production library, and unique date-specific episodes. No slideshow fallback.
Prepares one cross-platform Reel each day 2026-11-27 through 2026-12-10.
"""
import argparse
import json
import sys
from datetime import date,datetime,timedelta,timezone,time as daytime
from pathlib import Path
from meta_uniqueness import validate_unique, check_queue
from meta_discovery import decorate
from short_episode_specs import episode
from render_educational_short import render
from validate_youtube_video import validate

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"posts-queue.json"
LEDGER=ROOT/"publishing-log.json"
PKT=timezone(timedelta(hours=5))
RAW="https://raw.githubusercontent.com/hassan274-max/thetechnoz-social-media/main/"
VERSION="animated-educational-v2"

def prepare(day):
    if day<date(2026,11,27) or day>date(2026,12,10):
        raise RuntimeError(f"CONTENT_EXHAUSTED: no user-approved original animated Reel for {day}. "
                           "No old episode will be reused. Add and approve new scripts.")
    spec=episode(day)
    if not spec:
        raise RuntimeError(f"No approved original short video for {day}")
    queue=json.loads(QUEUE.read_text(encoding="utf-8"))
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    posts=queue["posts"]
    check_queue(posts)
    ident=f"{day.isoformat()}-reel"
    previous=next((p for p in posts if p.get("id")==ident),None)
    already=ledger.get("posts",{}).get(ident,{})
    if any(val.get("status")=="published" for val in already.values()):
        print(f"Reel {ident} was already published. No replacement, no re-upload.")
        return
    if previous and previous.get("creative_version")==VERSION:
        print(f"Reviewed Reel {ident} is already prepared; avoiding repeat.")
        return
    path=Path(f"assets/reel-{day.isoformat()}.mp4")
    # Render to a private temp filename first. A failed render never replaces
    # the existing asset or queue.
    import tempfile,shutil
    with tempfile.TemporaryDirectory(prefix="meta-animated-") as directory:
        candidate=Path(directory)/"candidate.mp4"
        render(spec,candidate)
        validate(candidate,"short")
        caption=(f"{spec['title']}\n\n{spec['question']}\n\n"
                 + " ".join(x[1] for x in spec["scenes"]) + "\n\n"
                 + spec["spoken_takeaway"]+"\n\n"+spec["closing_question"]
                 +"\n\nTheTechnoz Solutions — Where AI Meets Business."
                 +"\n\n#TheTechnozSolutions #ArtificialIntelligence #AmazonPPC #AmazonPrivateLabel #AI")
        caption=decorate(caption,spec["category"])
        when=datetime.combine(day,daytime(19,0),PKT).astimezone(timezone.utc)
        item={"id":ident,"kind":"reel","scheduled_at":when.isoformat().replace("+00:00","Z"),
              "video_url":RAW+str(path),"image_url":None,"path":str(path),
              "caption":caption,"platforms":["facebook","instagram"],
              "creative_version":VERSION,"editorial_id":spec["id"]}
        historic=[p for p in posts if p.get("id")!=ident]
        validate_unique(item,historic)
        # Preserve all historical records. Replace only unpublished placeholder
        # for this very same day, which prevents old 4.8s Reels going live.
        if previous:
            index=posts.index(previous)
            posts[index]=item
        else:
            posts.append(item)
        check_queue(posts)
        out=ROOT/path
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(candidate,out)
    QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Prepared animated 20-35 second Reel: {ident} | {spec['title']}")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--day-offset",type=int,default=0)
    args=parser.parse_args()
    prepare(datetime.now(PKT).date()+timedelta(days=args.day_offset))

if __name__=="__main__":main()
