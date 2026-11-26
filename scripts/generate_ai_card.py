#!/usr/bin/env python3
"""Generate a compact branded marketing card for AI automation."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT=Path("assets/ai-automation-20261126.png")
OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=1080,1350
im=Image.new("RGB",(W,H),(9,18,39))
d=ImageDraw.Draw(im)
for y in range(H):
    v=y/H
    d.line([(0,y),(W,y)],fill=(int(9+11*v),int(18+15*v),int(39+25*v)))
for x in range(-500,1300,150):
    d.line([(x,0),(x+700,H)],fill=(26,55,81),width=2)
d.rounded_rectangle((75,68,1005,1282),radius=46,outline=(45,126,188),width=3)
d.rounded_rectangle((119,105,961,187),radius=22,fill=(20,54,81))
def font(size,bold=True):
    for name in ([ "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()
def line(text,xy,size,color=(240,249,255),bold=True):
    d.text(xy,text,font=font(size,bold),fill=color)
line("THE TECHNOZ SOLUTIONS",(155,126),41,(201,239,255))
line("MAKE YOUR BUSINESS",(120,265),68)
line("WORK SMARTER.",(120,351),78,(76,217,243))
line("AI Automation  |  Practical Solutions",(123,473),34,(201,221,233),False)
d.rounded_rectangle((116,575,964,1064),radius=34,fill=(16,39,65),outline=(37,95,131),width=2)
items=[
    ("01", "Automate repetitive tasks"),
    ("02", "Turn data into decisions"),
    ("03", "Build intelligent workflows"),
    ("04", "Scale without extra complexity")
]
for i,(num,title) in enumerate(items):
    y=622+i*107
    d.rounded_rectangle((155,y,227,y+67),radius=16,fill=(28,112,155))
    line(num,(170,y+14),30)
    line(title,(253,y+11),35)
line("AI SERVICES   •   SAAS PRODUCTS   •   CONSULTING",(119,1120),27,(145,219,245))
d.line([(119,1203),(961,1203)],fill=(67,170,208),width=3)
line("Where AI Meets Business",(256,1221),32,(235,245,255),False)
im.save(OUT,optimize=True)
print(str(OUT))
