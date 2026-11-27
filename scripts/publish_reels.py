#!/usr/bin/env python3
"""Publish due queued 9:16 MP4 Reels to Facebook Pages and Instagram.
Uses the existing Meta Page token and the same published-ID ledger as images.
"""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from publish_meta import ROOT, QUEUE, LOG, TOKEN, ENABLED, DRY_RUN, IG_ID, graph, facebook_page_token, save, load, ensure_manifest, utcnow
from meta_uniqueness import check_queue
from meta_discovery import instagram_caption

def check_video(url):
    if not url.startswith("https://"):
        raise RuntimeError("Video URL must be HTTPS")
    req=urllib.request.Request(url,headers={"User-Agent":"TheTechnozSocialPublisher/1.0"})
    with urllib.request.urlopen(req,timeout=45) as resp:
        head=resp.read(32)
        mime=resp.headers.get("Content-Type","").split(";")[0].lower()
        if resp.status != 200 or b"ftyp" not in head[4:16]:
            raise RuntimeError(f"Hosted URL not a valid MP4 (HTTP {resp.status}, MIME {mime})")
        if mime not in ("video/mp4","application/octet-stream"):
            raise RuntimeError(f"Unexpected video Content-Type {mime}")

def upload_hosted_reel(video_id,url,page_access_token):
    endpoint=f"https://rupload.facebook.com/video-upload/v27.0/{video_id}"
    request=urllib.request.Request(endpoint,data=b"",method="POST",headers={
        "Authorization":"OAuth "+page_access_token,"file_url":url,
        "User-Agent":"TheTechnozSocialPublisher/1.0"})
    try:
        with urllib.request.urlopen(request,timeout=100) as response:
            data=json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Facebook Reel CDN upload HTTP {exc.code}") from None
    if not data.get("success"):
        raise RuntimeError("Facebook Reel CDN upload not confirmed")

def facebook_reel(url,caption):
    page_access_token=facebook_page_token()
    started=graph("POST","me/video_reels",{"upload_phase":"start"},token_override=page_access_token)
    vid=started["video_id"]
    upload_hosted_reel(vid,url,page_access_token)
    ended=graph("POST","me/video_reels",{
        "upload_phase":"finish","video_id":vid,"video_state":"PUBLISHED",
        "description":caption,"title":caption.splitlines()[0][:100]},token_override=page_access_token)
    if not ended.get("success"):
        raise RuntimeError("Facebook Reel finish was not confirmed")
    return vid

def instagram_reel(url,caption):
    created=graph("POST",f"{IG_ID}/media",{
        "media_type":"REELS","video_url":url,"caption":caption,
        "share_to_feed":"true"})
    container=created["id"]
    for _ in range(30):
        state=graph("GET",container,{"fields":"status_code,status"})
        if state.get("status_code")=="FINISHED":
            return graph("POST",f"{IG_ID}/media_publish",{"creation_id":container})["id"]
        if state.get("status_code") in ("ERROR","EXPIRED"):
            raise RuntimeError("Instagram Reel processing failed: "+str(state.get("status",""))[:160])
        time.sleep(15)
    raise RuntimeError("Instagram Reel processing timeout; verify published state before retry")

def main():
    if not ENABLED:
        sys.exit("Publishing disabled (PUBLISHING_ENABLED != true)")
    if not TOKEN and not DRY_RUN:
        sys.exit("Missing META_PAGE_ACCESS_TOKEN")
    queue=load(QUEUE,{"posts":[]}).get("posts",[])
    # Fail closed before any API publication if queued content repeats.
    check_queue(queue)
    ledger=load(LOG,{"posts":{}})
    failures=[]
    for post in queue:
        if post.get("kind")!="reel":continue
        ident=post.get("id","")
        try:
            when=datetime.fromisoformat(post["scheduled_at"].replace("Z","+00:00"))
        except (KeyError,ValueError):
            failures.append(f"{ident}: bad scheduled time")
            continue
        if when>utcnow():continue
        # Only publish the professionally animated 20-35 second reviewed Reels.
        # Legacy 4.8-second zoomed posters are not permitted in new posts.
        old_status=ledger.get("posts",{}).get(ident,{})
        if post.get("creative_version")!="animated-educational-v2":
            if all(old_status.get(target,{}).get("status")=="published" for target in post.get("platforms",[])):
                continue
            print(f"Legacy or unapproved Reel {ident} BLOCKED; no upload attempted.")
            continue
        url=post.get("video_url","")
        caption=post.get("caption","")
        targets=post.get("platforms",[])
        if not ident or not caption or not url or not set(targets).issubset({"facebook","instagram"}):
            failures.append(f"{ident}: invalid queue fields")
            continue
        status=ledger.setdefault("posts",{}).setdefault(ident,{})
        pending=[t for t in targets if status.get(t,{}).get("status")!="published"]
        if not pending:continue
        if DRY_RUN:
            print(f"DRY RUN: {ident} -> {pending}")
            continue
        try:check_video(url)
        except Exception as exc:
            failures.append(f"{ident}: video URL inaccessible: {exc}")
            continue
        for platform in pending:
            try:
                if platform=="facebook":
                    media_id=facebook_reel(url,caption)
                else:
                    media_id=instagram_reel(url,instagram_caption(caption,post.get("topic_category") or caption.splitlines()[0]))
                status[platform]={"status":"published","id":media_id,
                                  "published_at":utcnow().isoformat()}
                save(LOG,ledger)
                print(f"Published Reel {ident} -> {platform}: {media_id}")
            except Exception as exc:
                print(f"ERROR: Reel {ident} -> {platform}: {exc}")
                failures.append(f"{ident}/{platform}: {exc}")
        if targets and all(status.get(t,{}).get("status")=="published" for t in targets):
            ensure_manifest(post,utcnow())
    if failures:
        print(f"{len(failures)} Reel publishing errors. See logs.")
        sys.exit(1)
    print("Reel publishing workflow complete.")

if __name__=="__main__":
    main()
