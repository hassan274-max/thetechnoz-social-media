#!/usr/bin/env python3
"""Direct LinkedIn personal-profile poster; no scheduling service.

Requirements from LinkedIn developer app (stored only as Actions secrets):
LINKEDIN_ACCESS_TOKEN: user-authorized OAuth2 token with w_member_social scope
LINKEDIN_PERSON_URN: urn:li:person:<LinkedIn-person-id>
The tool exits without attempting publication unless LINKEDIN_DIRECT_ENABLED=true.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"linkedin-direct-queue.json"
LEDGER=ROOT/"linkedin-direct-log.json"

def main():
    if os.environ.get("LINKEDIN_DIRECT_ENABLED","").lower()!="true":
        print("Direct LinkedIn publishing not enabled; nothing uploaded.")
        return
    token=os.environ.get("LINKEDIN_ACCESS_TOKEN","").strip()
    author=os.environ.get("LINKEDIN_PERSON_URN","").strip()
    if not token or not author.startswith("urn:li:person:"):
        raise SystemExit("Missing verified LinkedIn OAuth access token or member URN; no upload")
    import datetime
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5)))
    items=json.loads(QUEUE.read_text())["posts"]
    ledger=json.loads(LEDGER.read_text())
    ready=[x for x in items if x["scheduled_at"]<=now.isoformat() and x["id"] not in ledger["posts"]]
    if not ready:
        print("No new due posts; never repeat older posts.")
        return
    if len(ready)>1:
        raise SystemExit("More than one overdue post; manual reconciliation required to avoid unexpected bulk posting")
    item=ready[0]
    if item.get("status")!="approved":
        raise SystemExit("Post is not approved")
    text=item["text"].strip()
    if not 40<=len(text)<=3000:
        raise SystemExit("Invalid post length")
    # Intentionally record claim before upload. An unclear outcome is never retried automatically.
    ledger["posts"][item["id"]]={"status":"attempted","claimed_at":now.isoformat(),
                                  "note":"Check LinkedIn feed before retrying."}
    LEDGER.write_text(json.dumps(ledger,indent=2)+"\n")
    # GitHub workflow must persist this claim BEFORE LinkedIn API is contacted.
    print("CLAIM_CREATED",item["id"])

if __name__=="__main__":main()
