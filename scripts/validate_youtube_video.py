#!/usr/bin/env python3
"""Pre-upload media checks. Fail closed if narration or video isn't usable."""
import argparse
import json
import math
import subprocess
from pathlib import Path

def validate(filename, kind):
    path=Path(filename)
    if not path.is_file() or path.stat().st_size<20_000:
        raise RuntimeError("Rendered MP4 missing or unexpectedly small")
    result=subprocess.run(
        ["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],
        capture_output=True,text=True,check=True)
    info=json.loads(result.stdout)
    streams=info.get("streams",[])
    videos=[s for s in streams if s.get("codec_type")=="video"]
    audios=[s for s in streams if s.get("codec_type")=="audio"]
    if len(videos)!=1 or len(audios)!=1:
        raise RuntimeError("Expected one video and one audible narration audio track")
    video, audio=videos[0],audios[0]
    expected=(720,1280) if kind=="short" else (1280,720)
    actual=(video.get("width"),video.get("height"))
    if actual!=expected:
        raise RuntimeError(f"Wrong video dimensions: expected {expected}, found {actual}")
    if video.get("codec_name")!="h264" or audio.get("codec_name")!="aac":
        raise RuntimeError("Expected H264 video and AAC audio codecs")
    seconds=float(info["format"]["duration"])
    lo,hi=(18,35) if kind=="short" else (300,480)
    if not lo<=seconds<=hi:
        raise RuntimeError(f"{kind} runtime {seconds:.1f}s outside {lo}-{hi}s")
    # Detect an empty or completely silent soundtrack without extracting/uploading.
    volume=subprocess.run(
        ["ffmpeg","-hide_banner","-i",str(path),"-vn","-af","volumedetect",
         "-f","null","-"],capture_output=True,text=True,check=True)
    import re
    m=re.search(r"max_volume:\s*(-?[\d.]+)\s*dB",volume.stderr)
    if not m or float(m.group(1)) < -45:
        raise RuntimeError("Narration audio is silent or below audible threshold")
    print(f"VALIDATION PASSED: {kind}, {seconds:.1f}s, {actual[0]}x{actual[1]}, "
          f"H.264/AAC; peak audio {m.group(1)} dB")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file",required=True)
    parser.add_argument("--kind",choices=["short","tutorial"],required=True)
    args=parser.parse_args()
    validate(args.file,args.kind)
