#!/usr/bin/env python3
"""Prepare two original, reusable branded assets for a date.
A daily educational photo at 11:00 PKT and a 5-second Reel at 19:00 PKT.
Curated evergreen copy; this is NOT live LLM content generation.
"""
import argparse
import json
import subprocess
import tempfile
from original_audio import build as build_original_audio
from meta_uniqueness import check_queue, validate_unique, normalized, headline
from datetime import datetime, timedelta, date, time as daytime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
QUEUE = ROOT / "posts-queue.json"
PKT = timezone(timedelta(hours=5))
RAW = "https://raw.githubusercontent.com/hassan274-max/thetechnoz-social-media/main/"

TOPICS = [
 ("AI", "AUTOMATE THE BORING WORK", "Spend less time copying data, more time making decisions.", "AI automation works best when a process is clearly defined. Start with one repetitive task, measure the time saved, and expand only when results are reliable."),
 ("Amazon PL", "CLICKS ARE NOT SALES", "Improve conversion before increasing bids.", "High traffic with low conversion? Check search-term relevance, pricing, reviews, delivery promise and listing quality before increasing your PPC budget."),
 ("AI", "YOUR DATA NEEDS CONTEXT", "Reliable AI starts with good business evidence.", "Before adding an AI assistant, clarify what data it can access, which decisions need human review and how accuracy will be measured."),
 ("Amazon PL", "RANKING STARTS WITH RELEVANCE", "Target keywords shoppers actually use.", "Organic keyword ranking isn't simply a function of ad spend. Relevance, conversion and consistent customer demand matter."),
 ("AI", "SMALL WORKFLOWS. BIG IMPACT.", "Automate one repeatable decision at a time.", "A useful AI workflow should have a clear input, a defined output, a human escalation path and measurable business impact."),
 ("Amazon PL", "WATCH UNIT SALES", "Orders alone can hide important trends.", "When reviewing Amazon campaigns, compare units sold, ad spend, conversion rate and profit—not just order count."),
 ("AI", "AI IS NOT A MAGIC BUTTON", "Good processes make better automations.", "An AI tool cannot fix an unclear workflow. Map the process, identify the bottleneck and automate the highest-value step first."),
 ("Amazon PL", "CHECK THE SEARCH TERMS", "Your targeting and shopper intent may differ.", "A keyword can look relevant but send low-quality traffic. Review actual search terms before deciding which bids to raise or reduce."),
 ("AI", "FROM REPORTS TO ACTIONS", "Turn analytics into repeatable business decisions.", "The goal of AI analytics isn't more dashboards. It's identifying what changed, why it matters and what action to test."),
 ("Amazon PL", "STOCKOUTS HURT GROWTH", "Inventory planning is a marketing decision too.", "A profitable Amazon campaign loses momentum when inventory runs out. Coordinate PPC pacing with stock and replenishment plans."),
 ("AI", "AUTOMATE WITH GUARDRAILS", "Speed matters. Accuracy matters more.", "For business automation, define limits, logging and manual approval for high-impact actions. Fast mistakes aren't efficiency."),
 ("Amazon PL", "LISTING IMAGES SELL", "Make the first image clear, not crowded.", "When your Amazon listing isn't converting, compare the value proposition, main image and competitor offer before rewriting every keyword."),
 ("AI", "AI + HUMAN JUDGMENT", "Better decisions come from both.", "Use AI to surface patterns and prepare recommendations, then verify them against real data and business constraints."),
 ("Amazon PL", "OPTIMIZE FOR PROFIT", "More sales are useful only when margins work.", "Measure advertising against contribution margins and business goals. TACOS, ad-attributed sales and unit velocity each tell part of the story.")
]

def font(size, bold=True):
    names = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    return ImageFont.truetype(names[0 if bold else 1], size)

def wrapped(draw, text, max_width, fnt):
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textbbox((0,0),candidate,font=fnt)[2] > max_width and line:
            lines.append(line); line = word
        else: line = candidate
    if line:lines.append(line)
    return lines

def create_poster(path, topic, hook, subtitle, square=False):
    w,h = (1080,1350) if square else (720,1280)
    im=Image.new("RGB",(w,h),(7,17,38)); draw=ImageDraw.Draw(im)
    for y in range(h):
        v=y/h
        draw.line([(0,y),(w,y)],fill=(int(7+10*v),int(17+18*v),int(38+22*v)))
    s=w/720
    margin=int(54*s)
    draw.rounded_rectangle([margin,int(65*s),w-margin,h-int(66*s)],radius=int(32*s),outline=(53,148,200),width=int(3*s))
    draw.rounded_rectangle([margin+int(30*s),int(105*s),w-margin-int(30*s),int(180*s)],radius=int(16*s),fill=(18,49,77))
    draw.text((margin+int(45*s),int(128*s)),"THE TECHNOZ SOLUTIONS",font=font(int(25*s)),fill=(220,244,255))
    draw.text((margin+int(35*s),int(265*s)),topic.upper()+"  /  INSIGHT",font=font(int(25*s)),fill=(66,221,240))
    y=int(350*s)
    for part in wrapped(draw,hook,int(w-margin*2-65*s),font(int(48*s))):
        draw.text((margin+int(35*s),y),part,font=font(int(48*s)),fill=(246,251,255))
        y+=int(69*s)
    y+=int(52*s)
    for part in wrapped(draw,subtitle,int(w-margin*2-75*s),font(int(29*s),False)):
        draw.text((margin+int(35*s),y),part,font=font(int(29*s),False),fill=(190,215,233))
        y+=int(48*s)
    draw.rounded_rectangle([margin+int(30*s),h-int(278*s),w-margin-int(30*s),h-int(151*s)],radius=int(23*s),fill=(20,64,91))
    draw.text((margin+int(55*s),h-int(234*s)),"AI  •  AMAZON PL  •  SAAS",font=font(int(22*s)),fill=(113,224,247))
    draw.text((margin+int(55*s),h-int(195*s)),"Where AI Meets Business",font=font(int(23*s),False),fill=(238,249,254))
    path.parent.mkdir(parents=True,exist_ok=True)
    im.save(path,optimize=True)

def make_video(poster, output):
    """Combine animated branded image with an original 4.8-second sonic logo."""
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="thetechnoz-audio-") as folder:
        wav_path=Path(folder)/"original-brand-sound.wav"
        build_original_audio(wav_path)
        command=[
            "ffmpeg","-hide_banner","-loglevel","error","-y",
            "-loop","1","-framerate","30","-i",str(poster),
            "-i",str(wav_path),
            "-filter_complex",
            "[0:v]zoompan=z='min(zoom+0.00024,1.045)':d=144:s=720x1280:fps=30,"
            "format=yuv420p[v]",
            "-map","[v]","-map","1:a","-frames:v","144",
            "-c:v","libx264","-preset","veryfast","-crf","24","-r","30",
            "-c:a","aac","-b:a","128k","-ar","48000","-ac","2",
            "-t","4.8","-movflags","+faststart",str(output)]
        subprocess.run(command,check=True)
    subprocess.run(["ffprobe","-v","error","-show_entries",
                    "stream=codec_type,codec_name:format=duration",
                    "-of","json",str(output)],check=True,stdout=subprocess.DEVNULL)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--day-offset",type=int,default=0)
    ap.add_argument("--reel-only",action="store_true",help="Prepare only Reel for immediate manual test")
    args=ap.parse_args()
    target=datetime.now(PKT).date()+timedelta(days=args.day_offset)
    queue=json.loads(QUEUE.read_text(encoding="utf-8"))
    history=queue.get("posts",[])
    # Never use modular arithmetic to recycle TOPICS. The queue is our
    # permanent historical audit even after old media assets are cleaned up.
    check_queue(history)
    datekey=target.isoformat()
    used={headline(p) for p in history}
    ids={p.get("id") for p in history}
    pending=[]
    # Alternate which topic category is used for the photo vs Reel each day.
    first_category="AI" if target.toordinal()%2==0 else "Amazon PL"
    second_category="Amazon PL" if first_category=="AI" else "AI"
    slots=[(11,"image",Path(f"assets/daily-{datekey}.png"),first_category),
           (19,"reel",Path(f"assets/reel-{datekey}.mp4"),second_category)]
    for hour,kind,path,category in slots:
        if args.reel_only and kind!="reel":
            continue
        ident=f"{datekey}-{kind}"
        if ident in ids:
            print(f"Already queued {ident}; not generating again")
            continue
        candidates=[t for t in TOPICS if t[0]==category and normalized(t[1]) not in used]
        if not candidates:
            raise RuntimeError(f"CONTENT_EXHAUSTED: no unused {category} topics for {kind}. "
                               "No post prepared. Add and review original topics before publishing.")
        t=candidates[0]
        used.add(normalized(t[1]))
        when=datetime.combine(target,daytime(hour),PKT).astimezone(timezone.utc)
        topic,hook,subtitle,body=t
        caption=(f"{hook}\n\n{body}\n\nTheTechnoz Solutions — Where AI Meets Business.\n\n"
                 "#TheTechnozSolutions #ArtificialIntelligence #AmazonPrivateLabel #AIAutomation #Ecommerce")
        entry={"id":ident,"kind":kind,"scheduled_at":when.isoformat().replace("+00:00","Z"),
               "image_url":RAW+str(path) if kind=="image" else None,
               "video_url":RAW+str(path) if kind=="reel" else None,
               "path":str(path),"caption":caption,
               "platforms":["facebook","instagram"]}
        validate_unique(entry,history+[record for record,_ in pending])
        pending.append((entry,t))
    if not pending:
        print("All requested slots already queued. No new items or duplicates.")
        return
    # Validate all entries before expensive rendering or changing the queue.
    for entry,t in pending:
        path=ROOT/entry["path"]
        if entry["kind"]=="image":
            create_poster(path,*t[:3],square=True)
        else:
            frame=ROOT/Path(f"assets/reel-frame-{datekey}.png")
            create_poster(frame,*t[:3])
            make_video(frame,path)
            frame.unlink()
        queue["posts"].append(entry)
    check_queue(queue["posts"])
    QUEUE.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Prepared {len(pending)} strictly unique posts for {target}; no topic reuse.")

if __name__=="__main__":
    main()
