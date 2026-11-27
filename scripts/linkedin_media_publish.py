#!/usr/bin/env python3
"""Scheduled personal LinkedIn media publishing; fail closed, never upload text-only."""
import argparse, datetime as dt, json, os, re, subprocess, sys, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PKT=dt.timezone(dt.timedelta(hours=5))
VERSION="202609"
API="https://api.linkedin.com/rest"
LEDGER=ROOT/"linkedin-direct-log.json"
META=ROOT/"posts-queue.json"
LI=ROOT/"linkedin-direct-queue.json"
def auth():
    token=os.getenv("LINKEDIN_ACCESS_TOKEN","").strip()
    if not token or any(ord(c)<33 or ord(c)>126 for c in token): raise RuntimeError("Missing/invalid LinkedIn access token")
    req=urllib.request.Request("https://api.linkedin.com/v2/userinfo",headers={"Authorization":"Bearer "+token})
    with urllib.request.urlopen(req,timeout=25) as response: subject=str(json.load(response).get("sub",""))
    if not re.fullmatch(r"[A-Za-z0-9_-]+",subject): raise RuntimeError("No authenticated member identity")
    return token,"urn:li:person:"+subject
def request(url,token,method="GET",body=None):
    headers={"Authorization":"Bearer "+token,"Linkedin-Version":VERSION,"X-Restli-Protocol-Version":"2.0.0"}
    if body is not None:headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,method=method,headers=headers,data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req,timeout=60) as resp:
        return resp.status,dict(resp.headers),json.loads(resp.read() or b"{}") if method!="PUT" else {}
def upload_image(path,token,owner):
    _,_,out=request(API+"/images?action=initializeUpload",token,"POST",{"initializeUploadRequest":{"owner":owner}})
    value=out["value"];data=path.read_bytes()
    req=urllib.request.Request(value["uploadUrl"],data=data,method="PUT",headers={"Authorization":"Bearer "+token,"Content-Type":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=120) as resp:
        if resp.status not in (200,201,202):raise RuntimeError("Image upload not acknowledged")
    return value["image"]
def upload_video(path,token,owner):
    data=path.read_bytes()
    _,_,out=request(API+"/videos?action=initializeUpload",token,"POST",{"initializeUploadRequest":{"owner":owner,"fileSizeBytes":len(data),"uploadCaptions":False,"uploadThumbnail":False}})
    value=out["value"];tags=[]
    for part in value["uploadInstructions"]:
        first,last=int(part["firstByte"]),int(part["lastByte"])
        req=urllib.request.Request(part["uploadUrl"],data=data[first:last+1],method="PUT",headers={"Content-Type":"application/octet-stream"})
        with urllib.request.urlopen(req,timeout=120) as resp:
            if resp.status not in (200,201,202):raise RuntimeError("Video part upload not acknowledged")
            etag=resp.headers.get("ETag","").strip().strip('"')
            if not etag:raise RuntimeError("Missing video upload ETag")
            tags.append(etag)
    request(API+"/videos?action=finalizeUpload",token,"POST",{"finalizeUploadRequest":{"video":value["video"],"uploadToken":value.get("uploadToken",""),"uploadedPartIds":tags}})
    return value["video"]
def save_ledger(ledger,note):
    LEDGER.write_text(json.dumps(ledger,indent=2)+"\n")
    subprocess.run(["git","add","linkedin-direct-log.json"],cwd=ROOT,check=True)
    subprocess.run(["git","commit","-m",note],cwd=ROOT,check=True)
    subprocess.run(["git","pull","--rebase","origin","main"],cwd=ROOT,check=True)
    subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT,check=True)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--slot",choices=["image","reel"],required=True)
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--now",action="store_true",help="Explicit one-time immediate image publish via GitHub trigger")
    args=parser.parse_args()
    now=dt.datetime.now(PKT); day=now.date().isoformat()
    planned=dt.datetime.combine(now.date(),dt.time(12 if args.slot=="image" else 19),PKT)
    if (now<planned or now-planned>dt.timedelta(hours=3)) and not args.now:
        print("Outside scheduled posting window; no upload");return
    key=day+"-"+args.slot
    if args.now:
        marker=json.loads((ROOT/"linkedin-post-now.json").read_text())
        if args.slot!="image" or marker.get("id")!=key or marker.get("date")!=day or marker.get("approved") is not True:
            raise RuntimeError("Immediate publishing not explicitly authorized for this item")
    meta=json.loads(META.read_text())["posts"]
    matches=[p for p in meta if p.get("id")==key and p.get("kind")==args.slot]
    if len(matches)!=1:raise RuntimeError("Missing unique, prepared Meta "+args.slot+" for "+day+"; no upload")
    source=matches[0]
    if source.get("creative_version") not in (None,"animated-educational-v2"):
        raise RuntimeError("Unapproved creative version")
    path=ROOT/source["path"]
    if path.resolve().is_relative_to((ROOT/"assets").resolve()) is False or not path.is_file() or path.stat().st_size<10000:
        raise RuntimeError("Approved media missing; no text-only fallback")
    expected=".png" if args.slot=="image" else ".mp4"
    if path.suffix!=expected:raise RuntimeError("Invalid media type")
    li=json.loads(LI.read_text())["posts"]
    # An original, LinkedIn-specific caption, matched by date/category when present.
    custom=[p for p in li if p.get("id")==key and p.get("status")=="approved"]
    if len(custom)>1:raise RuntimeError("Ambiguous LinkedIn caption")
    if custom:
        caption=custom[0]["text"].strip()
    else:
        caption=source["caption"].strip()
        if args.slot=="reel":caption+="\n\nOn LinkedIn, the key question is whether this concept changes a real workflow or decision."
        else:caption+="\n\nPractical takeaway: evaluate the result against reliable evidence before scaling the approach."
    if not 80<=len(caption)<=3000:raise RuntimeError("Invalid caption length")
    ledger=json.loads(LEDGER.read_text())
    if key in ledger["posts"]:
        print("Already claimed or published; no retry: "+key);return
    if args.dry_run:
        print("Ready:",key,"media:",str(path.relative_to(ROOT)),"caption chars:",len(caption));return
    if os.getenv("LINKEDIN_DIRECT_ENABLED","").lower()!="true":raise RuntimeError("Publishing disabled")
    token,owner=auth()
    ledger["posts"][key]={"personal":{"status":"attempted","at":dt.datetime.now(dt.timezone.utc).isoformat(),"kind":args.slot}}
    save_ledger(ledger,"chore: claim LinkedIn media "+key)
    media=upload_image(path,token,owner) if args.slot=="image" else upload_video(path,token,owner)
    payload={"author":owner,"commentary":caption,"visibility":"PUBLIC","distribution":{"feedDistribution":"MAIN_FEED","targetEntities":[],"thirdPartyDistributionChannels":[]},"lifecycleState":"PUBLISHED","isReshareDisabledByAuthor":False,"content":{"media":{"id":media}}}
    status,headers,_=request(API+"/posts",token,"POST",payload)
    post_id=headers.get("x-restli-id") or headers.get("X-RestLi-Id")
    if status not in (200,201) or not post_id:raise RuntimeError("Post result ambiguous; check LinkedIn feed manually")
    ledger=json.loads(LEDGER.read_text())
    ledger["posts"][key]={"personal":{"status":"published","post_id":post_id,"kind":args.slot,"at":dt.datetime.now(dt.timezone.utc).isoformat()}}
    save_ledger(ledger,"chore: confirm LinkedIn media "+key)
    print("Published",key,post_id)
if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("LinkedIn media publishing halted:",type(exc).__name__,str(exc)[:200],file=sys.stderr)
        sys.exit(1)
