#!/usr/bin/env python3
"""Render 27-second original full-screen RAG motion-graphics explainer.
No external images, font uploads, licensed footage or audio are required.
"""
import math, subprocess, wave, struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS,DURATION=720,1280,24,27
NAVY=(7,19,39);WHITE=(242,249,255);CYAN=(68,221,242);GREEN=(125,238,180);MUTED=(162,193,215)
SCENES=[0,4.4,9.1,15,21.2,27]
CAPTIONS=[
 "An AI can answer without enough evidence.",
 "RAG searches relevant documents.",
 "It selects the strongest passages.",
 "Evidence goes into the language model.",
 "Grounded answers still need verification."]
FONTS=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
def font(sz,bold=True):return ImageFont.truetype(FONTS[0 if bold else 1],sz)
def clamp(x):return max(0,min(1,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def text_center(d,xy,txt,size,color=WHITE,bold=True):
    f=font(size,bold); box=d.textbbox((0,0),txt,font=f)
    d.text((int(xy[0]-(box[2]-box[0])/2),int(xy[1]-(box[3]-box[1])/2)),txt,font=f,fill=color)
def lines(s,maxlen=31):
    words=s.split(); out=[];current=""
    for word in words:
        if len(current+" "+word)>maxlen and current:
            out.append(current);current=word
        else:current=(current+" "+word).strip()
    if current:out.append(current)
    return out
def panel(d,rect,fill=(17,44,69),line=CYAN,r=24):
    d.rounded_rectangle(tuple(map(int,rect)),radius=r,fill=fill,outline=line,width=3)
def arrow(d,from_pt,to_pt,p,color=CYAN):
    p=ease(p);x0,y0=from_pt;x1,y1=to_pt
    xx=x0+(x1-x0)*p;yy=y0+(y1-y0)*p
    d.line((x0,y0,xx,yy),fill=color,width=5)
    if p>.95:
        ang=math.atan2(y1-y0,x1-x0)
        d.polygon([(xx+11*math.cos(ang),yy+11*math.sin(ang)),
                   (xx-12*math.cos(ang+.5),yy-12*math.sin(ang+.5)),
                   (xx-12*math.cos(ang-.5),yy-12*math.sin(ang-.5))],fill=color)
def packet(d,from_pt,to_pt,t,col=GREEN):
    x0,y0=from_pt;x1,y1=to_pt;p=clamp(t)
    if p<=0 or p>=1:return
    x=x0+(x1-x0)*p;y=y0+(y1-y0)*p
    d.ellipse((x-9,y-9,x+9,y+9),fill=col)
    d.ellipse((x-15,y-15,x+15,y+15),outline=col,width=2)
def frame(t):
    im=Image.new("RGB",(W,H),NAVY);d=ImageDraw.Draw(im)
    for y in range(H):
        d.line((0,y,W,y),fill=(7+int(8*y/H),19+int(15*y/H),39+int(18*y/H)),width=1)
    for y in range(100,1280,150):d.line((0,y,W,y),fill=(18,39,63),width=1)
    for x in range(55,W,150):d.line((x,0,x,H),fill=(17,39,61),width=1)
    d.text((41,45),"THE TECHNOZ SOLUTIONS",font=font(27),fill=WHITE)
    d.text((41,87),"AI EXPLAINED VISUALLY",font=font(18,False),fill=CYAN)
    scene=max(0,min(4,sum(t>=s for s in SCENES[:-1])-1))
    local=t-SCENES[scene]
    length=SCENES[scene+1]-SCENES[scene]
    for j in range(5):
        d.rounded_rectangle((42+j*132,157,152+j*132,166),radius=4,fill=(24,67,92))
        if j<scene or j==scene:
            progress=1 if j<scene else clamp(local/length)
            d.rounded_rectangle((42+j*132,157,42+j*132+max(4,int(110*progress)),166),radius=4,fill=GREEN)
    headline=["WHEN AI GUESSES","STEP 1: RETRIEVE","STEP 2: SELECT","STEP 3: GENERATE","VERIFY SOURCES"][scene]
    text_center(d,(360,240),headline,39)
    # five scenes, each depicts the actual concept in motion
    if scene==0:
        panel(d,(92,356,627,535),line=(72,126,170))
        text_center(d,(360,399),"USER QUESTION",23,CYAN)
        text_center(d,(360,462),"What does my policy say?",26)
        panel(d,(123,660,596,885),line=(242,139,103))
        text_center(d,(360,712),"LLM RESPONSE",26)
        text_center(d,(360,771),"A confident claim...",25)
        text_center(d,(360,831),"NO SOURCE FOUND",21,(255,155,116))
        arrow(d,(360,540),(360,650),(local-.6)/1.1)
        for k in range(3):
            p=(local-2.0-k*.3)
            if p>0:packet(d,(360,560),(360,660),p,(255,155,116))
    if scene==1:
        panel(d,(73,330,648,450),line=CYAN)
        text_center(d,(360,390),"SEARCH QUERY",30)
        docx=[82,273,464]
        for i,x in enumerate(docx):
            dy=625+int(18*math.sin(local*1.4+i))
            panel(d,(x,dy,x+171,dy+200),line=GREEN if i==1 and local>2 else (72,140,175),r=17)
            d.rectangle((x+35,dy+35,x+135,dy+45),fill=(134,173,194))
            d.rectangle((x+35,dy+67,x+118,dy+78),fill=(88,129,160))
            d.rectangle((x+35,dy+98,x+139,dy+109),fill=(88,129,160))
            text_center(d,(x+84,dy+166),"DOC "+str(i+1),18)
            arrow(d,(360,455),(x+85,dy-16),(local-.6-i*.19)/1.6)
        if local>2.0:
            scan=82+int(clamp((local-2)/2.3)*520)
            d.rounded_rectangle((scan,581,scan+80,893),radius=13,outline=CYAN,width=3)
    if scene==2:
        for i,x in enumerate((81,268,455)):
            panel(d,(x,415,x+181,682),line=(73,132,167),r=17)
            text_center(d,(x+89,457),"SOURCE "+str(i+1),18,CYAN)
            for j in range(4):
                d.rectangle((x+25,494+34*j,x+155-(j%2)*30,503+34*j),fill=(77,125,154))
        move=ease((local-1.3)/1.3)
        panel(d,(86,790,633,920),fill=(20,66,68),line=GREEN)
        text_center(d,(360,835),"RELEVANT PASSAGE",26,GREEN)
        d.rounded_rectangle((130,862,590,878),radius=6,fill=GREEN if local>2 else (54,108,107))
        for j in range(4):
            packet(d,(360,660),(360,786),(local-2.3-j*.18)/1.2)
    if scene==3:
        panel(d,(61,415,310,657),line=GREEN);panel(d,(416,415,658,657),line=CYAN)
        text_center(d,(185,474),"EVIDENCE",26,GREEN)
        text_center(d,(538,474),"QUESTION",26,CYAN)
        for i in range(3):
            d.rectangle((102,523+i*30,273,531+i*30),fill=(120,188,167))
        text_center(d,(537,556),"What is true?",20)
        panel(d,(170,766,550,929),line=CYAN)
        text_center(d,(360,816),"LANGUAGE MODEL",25)
        text_center(d,(360,869),"EVIDENCE-INFORMED",19,GREEN)
        arrow(d,(190,667),(314,757),(local-.8)/1.2,GREEN)
        arrow(d,(533,667),(410,757),(local-1.0)/1.2,CYAN)
        for k in range(3):
            packet(d,(190,667),(314,757),(local-1.7-k*.22)/1.1)
    if scene==4:
        panel(d,(75,386,644,650),line=GREEN)
        text_center(d,(360,430),"ANSWER + REFERENCES",24,GREEN)
        for i in range(3):
            d.rounded_rectangle((120,481+i*51,570,504+i*51),radius=7,fill=(70,114,133))
        arrow(d,(360,667),(360,760),(local-.9)/.7,GREEN)
        panel(d,(111,786,615,950),line=CYAN)
        text_center(d,(360,841),"GROUNDED ≠ INFALLIBLE",24)
        text_center(d,(360,897),"CHECK THE EVIDENCE",23,GREEN)
    # full-frame readable subtitle, not a half-page text dump
    panel(d,(34,1095,686,1196),fill=(14,37,55),line=(49,109,141),r=17)
    for i,ln in enumerate(lines(CAPTIONS[scene],40)):
        text_center(d,(360,1137+i*36),ln,25)
    d.text((43,1230),"Where AI Meets Business",font=font(18,False),fill=MUTED)
    return im

def music(path):
    rate=32000;dur=DURATION
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate)
        b=bytearray()
        for n in range(rate*dur):
            t=n/rate
            amp=min(1,t/.6,(dur-t)/.7)
            # Original minimal ambient chord (no sampled third-party sounds)
            v=(.12*math.sin(2*math.pi*164.8*t)+.10*math.sin(2*math.pi*220*t)
               +.07*math.sin(2*math.pi*329.6*t)+.025*math.sin(2*math.pi*440*t))
            b+=struct.pack("<h",int(max(-1,min(1,v*max(0,amp)))*32767))
        f.writeframes(b)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",default="/tmp/rag-v3.mp4")
    args=p.parse_args();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    wav=out.with_suffix(".wav");music(wav)
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
         "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
         "-i",str(wav),"-c:v","libx264","-preset","veryfast","-crf","26",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","96k",
         "-t",str(DURATION),"-movflags","+faststart",str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(FPS*DURATION):
        try:proc.stdin.write(frame(i/FPS).tobytes())
        except BrokenPipeError:break
    proc.stdin.close()
    if proc.wait()!=0:raise RuntimeError("Video render failed")
    wav.unlink()
    print(f"Rendered {out}, {out.stat().st_size} bytes")
if __name__=="__main__":main()
