#!/usr/bin/env python3
"""Create original narrated YouTube Shorts and tutorials, then optionally upload.
Runs in GitHub Actions; no purchased music, footage, or voice models.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from youtube_editorial import scheduled_topic, scheduled_tutorial

ROOT=Path(__file__).resolve().parents[1]
CANVAS=(720,1280)
CHANNEL_ID="UCIwmarXnoB7vvssN9OxEeDA"

def run(args, capture=False):
    return subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE if capture else None).stdout

def font(size,bold=True):
    files=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    return ImageFont.truetype(files[0 if bold else 1],size)

def wrap(draw,text,ft,maxw):
    words=text.split()
    lines=[]; line=""
    for word in words:
        candidate=(line+" "+word).strip()
        if line and draw.textbbox((0,0),candidate,font=ft)[2]>maxw:
            lines.append(line); line=word
        else:line=candidate
    if line:lines.append(line)
    return lines

def slide(filepath,category,title,body,footer,wide=False):
    w,h=(1280,720) if wide else CANVAS
    im=Image.new("RGB",(w,h),(7,20,41));d=ImageDraw.Draw(im)
    for yy in range(h):
        d.line((0,yy,w,yy),fill=(7+int(yy/h*7),20+int(yy/h*14),41+int(yy/h*16)))
    m=70 if wide else 42
    d.rounded_rectangle((m,m,w-m,h-m),radius=30,outline=(57,147,200),width=3)
    d.text((m+35,m+36),"THE TECHNOZ SOLUTIONS",font=font(27 if wide else 23),fill=(224,247,255))
    d.text((m+35,m+120),category.upper()+"  /  EDUCATION",font=font(23),fill=(77,226,241))
    y=m+(138 if wide else 183)
    tfont=font(42 if wide else 49)
    for line in wrap(d,title.upper(),tfont,w-2*m-75):
        d.text((m+35,y),line,font=tfont,fill=(255,255,255))
        y+=58 if wide else 68
    y+=25 if wide else 45
    bfont=font(23 if wide else 31,False)
    max_lines=5 if wide else 13
    for line in wrap(d,body,bfont,w-2*m-75)[:max_lines]:
        d.text((m+35,y),line,font=bfont,fill=(198,220,236))
        y+=36 if wide else 48
    d.rounded_rectangle((m+30,h-m-110,w-m-30,h-m-29),radius=15,fill=(21,66,94))
    d.text((m+48,h-m-84),footer,font=font(21 if wide else 20),fill=(216,241,249))
    filepath.parent.mkdir(parents=True,exist_ok=True)
    im.save(filepath,optimize=True)

def speech(text,wav,rate=142):
    run(["espeak-ng","-v","en-us","-s",str(rate),"-p","46","-a","135","-w",str(wav),text])
    if not wav.exists() or wav.stat().st_size<500:
        raise RuntimeError("Narration generation failed")

def duration(path):
    raw=run(["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1",str(path)],capture=True)
    return float(raw.strip())

def segment(frame,wav,out,wide=False,min_sec=0):
    seconds=max(min_sec,duration(wav)+1.1)
    if wide:
        w,h=1280,720
    else:
        w,h=720,1280
    run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-loop","1","-framerate","24","-i",str(frame),"-i",str(wav),
        "-filter_complex",
        f"[0:v]scale={w}:{h},zoompan=z='min(zoom+0.00005,1.018)':d={int(math.ceil(seconds*24))}:s={w}x{h}:fps=24,format=yuv420p[v];"
        "[1:a]apad=pad_dur=3,volume=0.85[a]",
        "-map","[v]","-map","[a]","-t",f"{seconds:.2f}",
        "-c:v","libx264","-preset","ultrafast","-crf","29","-pix_fmt","yuv420p",
        "-r","24","-c:a","aac","-b:a","96k","-ar","44100",
        "-movflags","+faststart",str(out)])
    return seconds

def render(doc,out):
    wide=doc["kind"]=="tutorial"
    work=out.parent/"work"
    work.mkdir(parents=True,exist_ok=True)
    segments=[]
    if wide:
        chapters=[("INTRODUCTION",doc["title"],
                   "Welcome to TheTechnoz Solutions. Today we will work through an evidence-based approach, step by step."),
                  *[(name,name,body) for name,body in doc["chapters"]],
                  ("KEY TAKEAWAY","From evidence to action",
                   "Use these steps on real data, document your assumptions, and verify improvements through careful measurement.")]
    else:
        chapters=[
           ("THE QUESTION",doc["title"],doc["title"]+"."),
           ("THE EXPLANATION",doc["angle"],doc["narration"]),
           ("THE TAKEAWAY",doc["takeaway"],doc["takeaway"])
        ]
    for i,(heading,heading_text,voice_text) in enumerate(chapters):
        frame=work/f"slide{i:02d}.png"
        wav=work/f"voice{i:02d}.wav"
        clip=work/f"clip{i:02d}.mp4"
        visual=voice_text if wide else (doc["narration"] if i==1 else heading_text)
        slide(frame,doc["category"],heading_text,visual,
              "Where AI Meets Business  •  TheTechnoz Solutions",wide)
        speech(voice_text,wav,rate=112 if wide else 162)
        seconds=segment(frame,wav,clip,wide,min_sec=0)
        segments.append((clip,seconds))
    playlist=work/"playlist.txt"
    playlist.write_text("".join(f"file '{clip.resolve()}'\n" for clip,_ in segments))
    run(["ffmpeg","-hide_banner","-loglevel","error","-y",
         "-f","concat","-safe","0","-i",str(playlist),
         "-c","copy","-movflags","+faststart",str(out)])
    seconds=duration(out)
    if doc["kind"]=="short" and not 20 <= seconds <= 38:
        raise RuntimeError(f"Short is {seconds:.1f}s; expected roughly 20–30 seconds (maximum 38s)")
    if doc["kind"]=="tutorial" and not 270 <= seconds <= 600:
        raise RuntimeError(f"Tutorial is {seconds:.1f}s; target roughly 5–8 minutes; revise narration")
    return seconds

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",default=date.today().isoformat())
    p.add_argument("--kind",choices=["short","tutorial"],required=True)
    p.add_argument("--output",default="/tmp/thetechnoz-youtube-video.mp4")
    args=p.parse_args()
    day=date.fromisoformat(args.date)
    doc=scheduled_topic(day) if args.kind=="short" else scheduled_tutorial(day)
    if doc is None:
        raise SystemExit(f"No unused editorial script for {day} ({args.kind}); stopping safely without upload.")
    out=Path(args.output).resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    seconds=render(doc,out)
    print(f"RENDER SUCCESS: {out} | {seconds:.1f} seconds | {doc['title']}")
    info={
      "id":doc["id"],"kind":doc["kind"],"category":doc["category"],
      "title":doc["title"] + (" #Shorts" if args.kind=="short" else ""),
      "description":(
        (doc.get("narration") or "Detailed educational tutorial covering "+doc["title"])
        +"\n\nTheTechnoz Solutions | Where AI Meets Business.\n"
        +"#TheTechnozSolutions #AI #AmazonPrivateLabel"
        +("#Shorts" if args.kind=="short" else "")
      ),
      "file":str(out),"seconds":round(seconds,2)
    }
    (out.with_suffix(".json")).write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n")

if __name__=="__main__":
    main()
