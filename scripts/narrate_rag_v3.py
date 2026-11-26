#!/usr/bin/env python3
"""Mix original, free offline Kokoro-82M neural narration into the RAG V3 animation.
Requires local ONNX model/voices downloaded from the upstream open-source project.
No Google Cloud account, paid API, or private key is required.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

SCENES = [
    (0.0, 4.4, "An AI answer can sound confident without evidence."),
    (4.4, 9.1, "RAG searches trusted documents for relevant information."),
    (9.1, 15.0, "It selects the best passages for the language model."),
    (15.0, 21.2, "The model drafts an answer using that evidence."),
    (21.2, 27.0, "RAG improves grounding. Always verify the sources."),
]
VOICE = "am_adam"

def call(cmd, capture=False):
    r = subprocess.run(cmd, check=True, capture_output=capture, text=capture)
    return (r.stdout or "") if capture else ""

def seconds(path):
    return float(call(["ffprobe","-v","error","-show_entries","format=duration",
                       "-of","default=noprint_wrappers=1:nokey=1",str(path)],True).strip())

def render_voice(kokoro, text, path, voice):
    import soundfile as sf
    samples, sample_rate = kokoro.create(
        text, voice=voice, speed=1.0, lang="en-us")
    if len(samples) < 1000:
        raise RuntimeError("Kokoro generated empty/short audio")
    sf.write(str(path), samples, sample_rate)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--video",required=True,help="Existing V3 MP4 with instrumental")
    p.add_argument("--output",required=True)
    p.add_argument("--voice",default=VOICE)
    p.add_argument("--model",default="kokoro-v1.0.onnx")
    p.add_argument("--voices-file",default="voices-v1.0.bin")
    p.add_argument("--script-only",action="store_true",help="Print narration and scene timing, no credentials needed")
    args=p.parse_args()
    if args.script_only:
        for start,end,phrase in SCENES:
            print(f"{start:04.1f}–{end:04.1f}s: {phrase}")
        return
    video=Path(args.video)
    if not video.is_file():raise SystemExit(f"Missing existing V3 MP4: {video}")
    if abs(seconds(video)-27.0)>0.6:
        raise RuntimeError("Source video is not the approved 27-second V3 animation")
    from kokoro_onnx import Kokoro
    if not Path(args.model).is_file() or not Path(args.voices_file).is_file():
        raise RuntimeError("Missing Kokoro model files. Download model and voices before rendering.")
    kokoro=Kokoro(args.model,args.voices_file)
    with tempfile.TemporaryDirectory(prefix="rag-neural-") as td:
        root=Path(td)
        inputs=[]
        delayed=[]
        for i,(start,end,text) in enumerate(SCENES):
            wav=root/f"speech-{i}.wav"
            render_voice(kokoro,text,wav,args.voice)
            actual=seconds(wav)
            slot=end-start
            # Reserve a 160ms cushion per segment; never truncate sentences.
            speed=max(1.0,actual/max(.5,slot-.18))
            if speed>1.32:
                raise RuntimeError(
                    f"Scene {i+1} voice needs {actual:.2f}s for {slot:.2f}s; "
                    "shorten narration or lengthen animation instead of cutting speech.")
            inputs.extend(["-i",str(wav)])
            # Move voice into the allocated scene; fade boundaries and slight compression.
            delayed.append(
                f"[{i+1}:a]aresample=48000,atempo={speed:.4f},"
                f"afade=t=in:st=0:d=0.09,volume=1.15,"
                f"adelay={round((start+.08)*1000)}|{round((start+.08)*1000)}[s{i}]")
        # Retain the exact V3 video stream and lower music during narration.
        # At this stage the instrumental track is deliberately quiet throughout.
        filters=delayed+[
           f"{''.join(f'[s{i}]' for i in range(len(SCENES)))}"
           f"amix=inputs={len(SCENES)}:duration=longest:normalize=0,"
           "acompressor=threshold=0.12:ratio=2:attack=5:release=120[voice]",
           "[0:a]aresample=48000,volume=0.13[music]",
           "[music][voice]amix=inputs=2:duration=first:normalize=0,"
           "alimiter=limit=0.90[mix]"
        ]
        output=Path(args.output)
        output.parent.mkdir(parents=True,exist_ok=True)
        call(["ffmpeg","-hide_banner","-loglevel","error","-y",
              "-i",str(video),*inputs,
              "-filter_complex",";".join(filters),
              "-map","0:v:0","-map","[mix]","-c:v","copy",
              "-c:a","aac","-b:a","192k","-ac","2",
              "-t","27","-movflags","+faststart",str(output)])
        actual=seconds(output)
        if not 26.5<=actual<=27.5:
            raise RuntimeError("Unexpected narrated video duration")
        print(f"Neural narrated RAG V3 ready: {output} ({actual:.1f}s), voice={args.voice}")
        print("REVIEW REQUIRED: listen for pronunciation and check animation sync before upload.")
if __name__=="__main__":
    main()
