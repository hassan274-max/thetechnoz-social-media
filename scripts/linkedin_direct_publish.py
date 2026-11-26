#!/usr/bin/env python3
"""Direct LinkedIn personal-profile publisher via official Posts API.

No Metricool. Publish approved educational topics only to the personal profile.
Fail closed on missing scopes, connectivity errors,
ambiguous uploads and duplicate claim records. No silent retries.
Run only inside the scheduled trusted GitHub Actions workflow.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"linkedin-direct-queue.json"
LEDGER=ROOT/"linkedin-direct-log.json"
PERSON="personal"
TARGETS=(PERSON,)
PKT=dt.timezone(dt.timedelta(hours=5))
VERSION="202609"
URL="https://api.linkedin.com/rest/posts"

def git_save(note):
    subprocess.run(["git","add","linkedin-direct-log.json"],cwd=ROOT,check=True)
    subprocess.run(["git","commit","-m",note],cwd=ROOT,check=True)
    subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT,check=True)

def load():
    q=json.loads(QUEUE.read_text(encoding="utf-8"))
    log=json.loads(LEDGER.read_text(encoding="utf-8"))
    if not isinstance(q.get("posts"),list) or not isinstance(log.get("posts"),dict):
        raise RuntimeError("Broken direct LinkedIn queue or ledger")
    return q,log

def due_post(slot):
    q,log=load()
    now=dt.datetime.now(PKT)
    key=now.strftime("%Y-%m-%d")+"-"+slot
    if slot not in ("ai","amazon"):
        raise RuntimeError("Only approved AI and Amazon publishing slots are supported")
    posts=[p for p in q["posts"] if p.get("id")==key and p.get("status")=="approved"]
    if len(posts)!=1:
        print("No single approved item for",key,"—nothing to upload")
        return None
    p=posts[0]
    when=dt.datetime.fromisoformat(p["scheduled_at"])
    if not when.tzinfo or when.astimezone(PKT).date()!=now.date():
        raise RuntimeError("Invalid scheduled local date")
    if now<when.astimezone(PKT):
        print("Not due; nothing to upload")
        return None
    if now-when.astimezone(PKT)>dt.timedelta(hours=3):
        print("Too late to post safely; skipping expired slot")
        return None
    txt=p["text"].strip()
    if not 80<=len(txt)<=3000:
        raise RuntimeError("Invalid LinkedIn caption length")
    # Never recycle the same text in separate entries, including different dates.
    normalized=re.sub(r"\s+"," ",txt.casefold()).strip()
    for other in q["posts"]:
        if other["id"]!=key and re.sub(r"\s+"," ",other.get("text","").casefold()).strip()==normalized:
            raise RuntimeError("Repeated LinkedIn caption detected")
    return p

def author(target):
    if target!=PERSON:
        raise RuntimeError("Company Page publishing is not in scope")
    urn=os.getenv("LINKEDIN_PERSON_URN","").strip()
    pattern=r"urn:li:person:[A-Za-z0-9_-]+"
    if not re.fullmatch(pattern,urn):
        raise RuntimeError("Missing verified LinkedIn "+target+" author URN")
    return urn

def token():
    x=os.getenv("LINKEDIN_ACCESS_TOKEN","").strip()
    if not x:
        raise RuntimeError("Missing LINKEDIN_ACCESS_TOKEN; no upload attempted")
    return x

def post(target,p):
    author_urn=author(target)
    access=token()
    payload={
       "author":author_urn,
       "commentary":p["text"],
       "visibility":"PUBLIC",
       "distribution":{"feedDistribution":"MAIN_FEED","targetEntities":[],"thirdPartyDistributionChannels":[]},
       "lifecycleState":"PUBLISHED",
       "isReshareDisabledByAuthor":False,
    }
    req=urllib.request.Request(URL,
        data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization":"Bearer "+access,
            "Content-Type":"application/json",
            "Linkedin-Version":VERSION,
            "X-Restli-Protocol-Version":"2.0.0",
        },method="POST")
    try:
        with urllib.request.urlopen(req,timeout=45) as response:
            if response.status not in (200,201):
                raise RuntimeError("LinkedIn did not acknowledge post creation")
            post_id=response.headers.get("x-restli-id","").strip()
            if not post_id:
                raise RuntimeError("LinkedIn acknowledged post without an ID; inspect personal feed before retry")
            return post_id
    except urllib.error.HTTPError as exc:
        # No response body: API error bodies could include private metadata.
        raise RuntimeError("LinkedIn API rejected "+target+" post, HTTP "+str(exc.code)) from None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--slot",choices=["ai","amazon"],required=True)
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()
    q,log=load()
    p=due_post(args.slot)
    if p is None:return
    if args.dry_run:
        print("Safe dry run:",p["id"],"destination: personal")
        return
    if os.environ.get("LINKEDIN_DIRECT_ENABLED","").lower()!="true":
        print("LinkedIn direct publishing is not enabled. No API post attempted.")
        return
    # Require the authorized personal member ID before any side effects.
    for t in TARGETS:author(t)
    token()
    for target in TARGETS:
        q,log=load()
        item_log=log["posts"].setdefault(p["id"],{})
        if target in item_log:
            print("Skipping claimed/published destination",target,"for",p["id"])
            continue
        item_log[target]={
           "status":"attempted",
           "at":dt.datetime.now(dt.timezone.utc).isoformat(),
           "note":"If result is uncertain, manually check LinkedIn feed. No automatic retry."}
        LEDGER.write_text(json.dumps(log,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        git_save("chore: claim direct LinkedIn "+p["id"]+" "+target)
        post_id=post(target,p)
        # Persist confirmed API identifier immediately; this is distinct per target.
        q,log=load()
        log["posts"][p["id"]][target]={
          "status":"published","post_id":post_id,
          "at":dt.datetime.now(dt.timezone.utc).isoformat()}
        LEDGER.write_text(json.dumps(log,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        git_save("chore: confirm direct LinkedIn "+p["id"]+" "+target)
        print("LinkedIn published",p["id"],target,"post_id",post_id)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("Direct LinkedIn publisher halted:",str(exc)[:220],file=sys.stderr)
        sys.exit(1)
