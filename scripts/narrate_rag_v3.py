#!/usr/bin/env python3
"""Mix natural Google Cloud Chirp3 HD narration into the approved RAG V3 animation.

Original V3 timing remains unchanged. Requires a separate Google Cloud
Text-to-Speech service-account identity (NOT the YouTube OAuth token).
The Google credentials can come from GOOGLE_TTS_SERVICE_ACCOUNT_JSON or ADC.
No voice generation is attempted when credentials are absent.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

SCENES = [
    (0.0, 4.4, "An AI answer can sound convincing, even when its evidence is missing."),
    (4.4, 9.1, "RAG starts by searching trusted documents related to your question."),
    (9.1, 15.0, "It selects relevant passages and sends them to the language model."),
    (15.0, 21.2, "The model uses this context to draft an answer linked to its sources."),
    (21.2, 27.0, "RAG improves grounding, but you should still check the cited evidence."),
]
VOICE = "en-US-Chirp3-HD-Charon"

def call(cmd, capture=False):
    r = subprocess.run(cmd, check=True, capture_output=capture, text=capture)
    return (r.stdout or "") if capture else ""

def seconds(path):
    return float(call(["ffprobe","-v","error","-show_entries","format=duration",
                       "-of","default=noprint_wrappers=1:nokey=1",str(path)],True).strip())

def tts_client():
    from google.cloud import texttospeech
    raw = os.getenv("GOOGLE_TTS_SERVICE_ACCOUNT_JSON","").strip()
    if raw:
        from google.oauth2 import service_account
        try:
            info=json.loads(raw)
            if info.get("type") != "service_account":
                raise ValueError("The TTS secret must be a service account JSON")
            credentials=service_account.Credentials.from_service_account_info(info)
        except (ValueError, KeyError) as e:
            raise RuntimeError(f"Invalid Google TTS credential format: {type(e).__name__}") from None
        return texttospeech.TextToSpeechClient(credentials=credentials), texttospeech
    # Google Application Default Credentials; useful for local testing.
    return texttospeech.TextToSpeechClient(), texttospeech

def render_voice(client,tts,text,path,voice):
    response=client.synthesize_speech(
       request={"input":tts.SynthesisInput(text=text),
                "voice":tts.VoiceSelectionParams(language_code="en-US",name=voice),
                "audio_config":tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)})
    if not response.audio_content:
        raise RuntimeError("Cloud TTS returned empty audio")
    path.write_bytes(response.audio_content)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--video",required=True,help="Existing V3 MP4 with instrumental")
    p.add_argument("--output",required=True)
    p.add_argument("--voice",default=VOICE)
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
    client,tts=tts_client()
    with tempfile.TemporaryDirectory(prefix="rag-neural-") as td:
        root=Path(td)
        inputs=[]
        delayed=[]
        for i,(start,end,text) in enumerate(SCENES):
            wav=root/f"speech-{i}.wav"
            render_voice(client,tts,text,wav,args.voice)
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
