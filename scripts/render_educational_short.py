#!/usr/bin/env python3
"""Render topic-aware original animated YouTube Shorts with free Kokoro voice.

Full-frame vertical output; five scenes: hook, 3 visual explanations, takeaway/Q&A.
Original music is generated locally. Fail closed for unavailable visual scripts.
"""
import argparse, math, os, struct, subprocess, sys, tempfile, wave
from datetime import date
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from short_episode_specs import episode
from short_visual_stories import story_for, draw as draw_story, intro as draw_intro

W,H,FPS=720,1280,18
BG=(6,18,37);FG=(246,252,255);CYAN=(84,222,244)
MINT=(113,235,176);MUTED=(173,200,220);ORANGE=(255,178,108)
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTS={}
def font(size,bold=True):
    key=(size,bold)
    if key not in FONTS:FONTS[key]=ImageFont.truetype(BOLD if bold else REGULAR,size)
    return FONTS[key]
def clamp(n):return max(0.,min(1.,n))
def smooth(n):n=clamp(n);return n*n*(3-2*n)
def center(d,y,msg,size=30,color=FG,bold=True):
    f=font(size,bold);box=d.textbbox((0,0),msg,font=f)
    x=(W-(box[2]-box[0]))/2
    d.text((int(x),int(y)),msg,font=f,fill=color)
def in_card(d,rect,y,msg,size=22,color=FG,bold=True):
    """Center text in its own box, not across the full video width."""
    x0,_,x1,_=rect
    f=font(size,bold)
    box=d.textbbox((0,0),msg,font=f)
    width=box[2]-box[0]
    if width > (x1-x0-24):
        raise RuntimeError(f"Diagram label does not fit its node: {msg!r}")
    d.text((int((x0+x1-width)/2),int(y)),msg,font=f,fill=color)

def wrap(d,s,maxwidth,f):
    arr=[];line=""
    for word in s.split():
        test=(line+" "+word).strip()
        if line and d.textbbox((0,0),test,font=f)[2]>maxwidth:
            arr.append(line);line=word
        else:line=test
    if line:arr.append(line)
    return arr
def blocks(d,txt,top,size,color=FG,spacing=15,maxwidth=620):
    ft=font(size);arr=wrap(d,txt,maxwidth,ft)
    if len(arr)>5:raise RuntimeError("Text exceeds safe layout; rewrite this episode")
    for i,line in enumerate(arr):center(d,top+i*(size+spacing),line,size,color)
def card(d,rect,border=CYAN,fill=(18,48,70),r=22):
    d.rounded_rectangle(tuple(int(x) for x in rect),radius=r,fill=fill,outline=border,width=3)
def arrow(d,a,b,progress,color=CYAN):
    p=smooth(progress)
    if not p:return
    to=(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p)
    d.line((*a,*to),fill=color,width=5)
    if p>.92:d.ellipse((b[0]-9,b[1]-9,b[0]+9,b[1]+9),fill=color)
def dot(d,a,b,t,color=MINT):
    if t<=0 or t>=1:return
    x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
    d.ellipse((x-11,y-11,x+11,y+11),fill=color)
def visual(d,kind,t):
    """Meaningful motion diagrams: different scenes illustrate distinct mechanics."""
    p=smooth(t/1.6)
    if kind in ("traffic","conversion","tacos","margin","profit","budget","inventory","timeline"):
        # Charts with directionally illustrative values, no numerical performance claims.
        d.line((94,890,636,890),fill=(83,135,166),width=4)
        if kind in ("traffic","conversion","tacos","profit","margin"):
            heights=(140,230,170,280) if kind=="traffic" else (235,160,270,200)
            if kind=="conversion":heights=(240,100,185,145)
            for i,h in enumerate(heights):
                x=135+i*135
                d.rounded_rectangle((x,890-max(3,h*p),x+67,889),radius=2,
                   fill=CYAN if i%2==0 else MINT)
            center(d,950,"ILLUSTRATIVE METRICS",20,MUTED)
        else:
            for i in range(6):
                x=102+82*i
                fill=MINT if (kind=="inventory" and i<3) or (kind!="inventory" and i<4) else (44,78,103)
                card(d,(x,648,x+62,731),fill=fill,border=fill,r=11)
            arrow(d,(107,825),(614,825),t/2.3)
            center(d,950,"CHECK CAPACITY OVER TIME",20,MUTED)
    elif kind in ("retrieval","evidence","generation","vectors","lexical","hybrid","memory","storage","query"):
        # Never use full-canvas centering for node labels: it causes text collisions.
        left=(69,556,297,744)
        right=(421,556,649,744)
        card(d,left,border=MINT)
        card(d,right,border=CYAN)
        labels={
            "retrieval":("DOCUMENTS","RETRIEVER"),
            "evidence":("PASSAGES","EVIDENCE"),
            "generation":("CONTEXT","LANGUAGE MODEL"),
            "vectors":("EMBEDDINGS","VECTOR INDEX"),
            "lexical":("KEYWORDS","EXACT MATCH"),
            "hybrid":("KEYWORD HIT","SEMANTIC HIT"),
            "memory":("CONTEXT","SAVED STATE"),
            "storage":("FACTS","DATA STORE"),
            "query":("SEARCH TERM","MATCHED TEXT"),
        }
        a,b=labels[kind]
        size_a=17 if len(a)>11 else 19
        size_b=16 if len(b)>11 else 19
        in_card(d,left,583,a,size_a,MINT)
        in_card(d,right,583,b,size_b,CYAN)
        for node in (left,right):
            x0,y0,x1,y1=node
            for j in range(3):
                y=638+j*26
                width=(x1-x0-58)-j*16
                d.rounded_rectangle((x0+29,y,x0+29+width,y+9),
                                     radius=4,fill=(73,121,143))
        # Directional data packets travel in the clear gap between boxes.
        arrow(d,(302,647),(416,647),t/1.6)
        for j in range(3):
            dot(d,(306,647),(414,647),(t-1.3-j*.29)/1.1)
        if kind in ("evidence","hybrid","lexical"):
            node=(169,824,551,904)
            card(d,node,border=MINT,fill=(17,62,61))
            in_card(d,node,850,"VERIFY SOURCE SUPPORT",19,MINT)
    elif kind in ("agent","limits","stop","workflow","eval"):
        xs=(93,309,525)
        labels=("INPUT","CHECK","STOP" if kind in ("limits","stop") else "OUTPUT")
        for i,x in enumerate(xs):
            node=(x,624,x+102,746)
            card(d,node,border=MINT if i==2 else CYAN,r=17)
            in_card(d,node,662,labels[i],15)
            d.ellipse((x+37,703,x+65,731),outline=MINT if i==2 else CYAN,width=3)
        for i in range(2):
            arrow(d,(xs[i]+108,685),(xs[i+1]-7,685),(t-i*.45)/1.25,
                  MINT if i else CYAN)
        if kind in ("limits","stop"):
            center(d,864,"TIME • COST • VALIDATION",22,MINT)
        else:
            center(d,864,"TEST EACH STEP",22,MINT)
    elif kind in ("listing","ranking","target","diagnose"):
        card(d,(220,525,500,828),border=CYAN)
        d.rectangle((252,557,468,682),fill=(46,112,146))
        d.rounded_rectangle((282,603,440,642),radius=13,fill=MINT)
        for i in range(3):d.rectangle((254,715+i*25,439-i*20,723+i*25),fill=(121,166,185))
        for i in range(4):
            tt=(t-.6-i*.32)/1.6
            if 0<=tt<=1:dot(d,(70,676),(210,676),tt)
        center(d,901,"CLICK → LISTING → ACTION",21,MUTED)
    else:
        # No silent fallback to generic/unreviewed scenes.
        raise RuntimeError("Unreviewed animation type: "+str(kind))

def frame(spec,stage,progress,t,durations):
    theme=story_for(spec)
    accent,secondary,base=theme[4],theme[5],theme[6]
    im=Image.new("RGB",(W,H),base);d=ImageDraw.Draw(im)
    for y in range(H):
        d.line((0,y,W,y),fill=tuple(min(255,c+int(y/H*13)) for c in base))
    # Soft radial accents support distinctive editorial color per episode.
    for k in range(5):
        x=76+k*134
        d.line((x,190,x,1020),fill=tuple(min(255,c+17) for c in base),width=1)
    d.text((44,43),"THE TECHNOZ SOLUTIONS",font=font(25),fill=FG)
    d.text((44,84),"WHERE AI MEETS BUSINESS",font=font(17,False),fill=accent)
    category=spec["category"].upper()
    d.rounded_rectangle((490,73,673,116),radius=14,fill=tuple(min(255,c+30) for c in base))
    d.text((512,84),category if len(category)<12 else "TECH",font=font(16),fill=secondary)
    for i in range(5):
        a=45+i*128;b=a+111
        d.rounded_rectangle((a,166,b,174),radius=4,fill=(26,66,85))
        if i<stage or i==stage:
            d.rounded_rectangle((a,166,a+max(4,int(111*(1 if i<stage else clamp(progress)))),174),
                                radius=4,fill=accent)
    if stage==0:
        openings=("THE CHALLENGE","WHAT IF?","A QUESTION FOR YOU","LET'S INVESTIGATE")
        index=(date.fromisoformat(spec["id"][6:])-date(2026,11,27)).days
        center(d,248,openings[index%4],27,accent)
        blocks(d,spec["question"],339,34,FG,14)
        draw_intro(d,spec,t)
    elif stage<=3:
        label,spoken,kind=spec["scenes"][stage-1]
        center(d,246,f"{label}",31,accent)
        draw_story(d,spec,stage-1,t)
        card(d,(39,931,681,1060),border=accent,fill=tuple(min(255,c+15) for c in base))
        blocks(d,spoken,958,25,FG,9,600)
    else:
        center(d,249,"THE TAKEAWAY",27,accent)
        blocks(d,spec["spoken_takeaway"],356,32,secondary,14)
        card(d,(52,644,668,904),border=accent)
        center(d,688,"YOUR TURN",24,accent)
        blocks(d,spec["closing_question"],757,28,FG,10,560)
        for i in range(4):
            x=150+i*125
            d.ellipse((x-10,968-6*math.sin(t*3+i),x+10,988-6*math.sin(t*3+i)),fill=secondary)
    d.text((46,1124),"TheTechnoz Solutions  •  Where AI Meets Business",font=font(16,False),fill=MUTED)
    return im

def generate_voice(kokoro,spoken):
    samples,rate=kokoro.create(spoken,voice=os.getenv("KOKORO_VOICE","am_adam"),
                               speed=1.0,lang="en-us")
    if not len(samples):raise RuntimeError("Empty Kokoro output")
    a=np.asarray(samples,dtype=np.float32)
    if a.ndim>1:a=a.mean(axis=1)
    return a,rate

def audio_and_duration(spec,folder):
    from kokoro_onnx import Kokoro
    model=Path(os.getenv("KOKORO_MODEL","kokoro-v1.0.onnx"))
    voices=Path(os.getenv("KOKORO_VOICES","voices-v1.0.bin"))
    if not model.is_file() or not voices.is_file():raise RuntimeError("Kokoro model files missing")
    kokoro=Kokoro(str(model),str(voices))
    texts=[spec["question"],*[x[1] for x in spec["scenes"]],
           spec["spoken_takeaway"]+" "+spec["closing_question"]]
    segments=[];lengths=[];sample_rate=None
    for idx,spoken in enumerate(texts):
        audio,sr=generate_voice(kokoro,spoken)
        if sample_rate is None:sample_rate=sr
        if sr!=sample_rate:raise RuntimeError("Unexpected voice sample rate mismatch")
        # Short silence at beginning plus enough time for scene emphasis.
        seconds=max(4.0,len(audio)/sr+.72)
        if idx==4:seconds=max(6.3,len(audio)/sr+.86)
        if seconds>8.1:raise RuntimeError(f"Scene {idx+1} narration too long: {seconds:.1f}s")
        arr=np.zeros(round(seconds*sr),dtype=np.float32)
        st=int(.26*sr);arr[st:st+len(audio)]=audio[:len(arr)-st]
        segments.append(arr)
        lengths.append(seconds)
    allvoice=np.concatenate(segments)
    total=len(allvoice)/sample_rate
    if not (20<=total<=36):raise RuntimeError(f"Unacceptable Short duration {total:.1f}s")
    path=folder/"voice.wav";sf.write(str(path),allvoice,sample_rate)
    return path,lengths,total

def background(path,total):
    rate=24000;n=int(total*rate)
    with wave.open(str(path),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(rate)
        buf=bytearray()
        for i in range(n):
            t=i/rate
            fade=min(1,t/.6,(total-t)/.8)
            note=(.16*math.sin(2*math.pi*164.81*t)+
                  .09*math.sin(2*math.pi*220*t)+
                  .06*math.sin(2*math.pi*329.63*t))
            buf+=struct.pack("<h",round(32767*note*max(0,fade)))
        out.writeframes(buf)

def render(spec,out):
    with tempfile.TemporaryDirectory(prefix="technoz-short-") as folder:
        folder=Path(folder)
        voice,lengths,total=audio_and_duration(spec,folder)
        music=folder/"music.wav";background(music,total)
        cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
             "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
             "-r",str(FPS),"-i","-",
             "-i",str(voice),"-i",str(music),
             "-filter_complex","[1:a]volume=1.2[voice];[2:a]volume=0.14[music];"
                               "[voice][music]amix=inputs=2:duration=first:normalize=0,"
                               "alimiter=limit=0.92[outa]",
             "-map","0:v","-map","[outa]","-c:v","libx264",
             "-preset","veryfast","-crf","25","-pix_fmt","yuv420p",
             "-c:a","aac","-b:a","160k","-t",str(total),
             "-movflags","+faststart",str(out)]
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        frames=round(total*FPS);stages=[sum(lengths[:i]) for i in range(6)]
        for i in range(frames):
            t=i/FPS
            stage=max(0,min(4,sum(t>=x for x in stages[:-1])-1))
            local=t-stages[stage]
            ratio=local/lengths[stage]
            try:proc.stdin.write(frame(spec,stage,ratio,local,lengths).tobytes())
            except BrokenPipeError:break
        proc.stdin.close()
        if proc.wait():raise RuntimeError("FFmpeg motion/audio render failed")
        if not out.exists() or out.stat().st_size<30000:raise RuntimeError("Empty final video")
        print(f"RENDER SUCCESS {out} | {total:.1f}s | {spec['title']}")
        return total

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--date",required=True)
    parser.add_argument("--output",default="/tmp/thetechnoz-youtube-video.mp4")
    args=parser.parse_args()
    spec=episode(date.fromisoformat(args.date))
    if spec is None:raise SystemExit("No reviewed episode for selected date; skipping")
    out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    render(spec,out)
if __name__=="__main__":main()
