#!/usr/bin/env python3
"""Fail-closed duplication checks for Facebook and Instagram posts.

Never reuse an earlier topic headline, substantive caption, or creative asset
under a new post ID. Posting one approved queue item to Facebook AND Instagram
is intentional cross-posting, not repetition.
"""
import re

def normalized(value):
    return re.sub(r"\s+", " ", (value or "").casefold()).strip()

def headline(post):
    return normalized((post.get("caption") or "").splitlines()[0])

def body(post):
    return normalized(post.get("caption"))

def asset(post):
    return normalized(post.get("path") or post.get("video_url") or post.get("image_url"))

def validate_unique(new_post, history, require_unique_headline=True):
    """Block a duplicate across different queue IDs. Same ID is safe for retries."""
    ident=new_post.get("id")
    if not ident:
        raise ValueError("Missing post ID")
    head=headline(new_post)
    content=body(new_post)
    resource=asset(new_post)
    if not head or not content or not resource:
        raise ValueError(f"Missing content/asset for {ident}")
    for previous in history:
        if previous.get("id")==ident:
            continue
        phead=headline(previous)
        if require_unique_headline and phead and head==phead:
            raise ValueError(f"Repeated topic headline: {ident} conflicts with {previous.get('id')}")
        if body(previous)==content:
            raise ValueError(f"Repeated caption: {ident} conflicts with {previous.get('id')}")
        if asset(previous)==resource:
            raise ValueError(f"Reused creative asset: {ident} conflicts with {previous.get('id')}")
    return True

def check_queue(queue):
    seen=[]
    for item in queue:
        validate_unique(item,seen)
        seen.append(item)
    return True
