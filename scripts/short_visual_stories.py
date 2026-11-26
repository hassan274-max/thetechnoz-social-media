#!/usr/bin/env python3
"""Bespoke animated storyboards for TheTechnoz Solutions Shorts.

Original vector drawings (Pillow) with people, packages, trucks, charts,
document cards, retrieval nodes, storefronts, robots and safety controls.
Each episode has its own theme, stage-specific compositions and opening.
"""
import math
from datetime import date
from PIL import ImageDraw, ImageFont

# All colors are RGB tuples. Every episode changes composition AND palette.
STORIES = [
    ("RAG / evidence","library","scan","answer", (62,205,211),(245,161,92), (8,27,43)),
    ("PPC / shopper","ad","shopper","metrics", (255,174,94),(102,212,188),(33,26,44)),
    ("Agent safety","bot","stopwatch","human_review",(158,149,252),(105,214,242),(22,24,55)),
    ("Profit / cost","receipts","fees","profit",(253,185,110),(115,209,174),(34,29,37)),
    ("Hybrid search","semantic","exact","merge",(86,210,255),(243,143,196),(13,27,57)),
    ("Search intent","keyword","person_search","filters",(255,158,101),(249,207,105),(37,27,36)),
    ("RAG testing","test_set","citation_check","score",(169,216,123),(95,201,231),(18,34,45)),
    ("Budget pacing","coins","timeline","opportunity",(247,196,83),(122,213,230),(29,32,52)),
    ("Agent security","prompt","shield","attack",(184,158,249),(254,161,127),(32,25,52)),
    ("Product imagery","ad","product","shopping_cart",(236,158,105),(137,202,254),(29,32,43)),
    ("Agent vs flow","workflow","bot","human_review",(141,218,225),(245,189,106),(16,34,49)),
    ("Organic ranking","storefront","person_search","metrics",(93,205,170),(241,188,113),(13,40,43)),
    ("Context / memory","chat","archive","recall",(165,171,250),(132,222,201),(30,29,58)),
    ("Inventory / logistics","shopping_cart","warehouse","truck",(244,164,104),(111,210,229),(27,33,44)),
]
def story_for(spec):
    key=(date.fromisoformat(spec["id"].replace("short-",""))-date(2026,11,27)).days
    if not 0<=key<len(STORIES):raise RuntimeError("Missing original art direction for episode")
    return STORIES[key]

def ease(x):
    x=max(0,min(1,x))
    return x*x*(3-2*x)
def circle(d,x,y,r,fill,outline=None,width=2):
    d.ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=fill,outline=outline,width=width)
def box(d,rect,color,rounding=15,outline=None):
    d.rounded_rectangle(tuple(map(int,rect)),radius=rounding,fill=color,outline=outline,width=3)
def label(d,xy,s,font,color):
    d.text(tuple(map(int,xy)),s,font=font,fill=color)
def centered(d,x,y,s,font,color):
    bb=d.textbbox((0,0),s,font=font)
    label(d,(x-(bb[2]-bb[0])/2,y),s,font,color)
def f(size=22,bold=True):
    name="/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf"
    return ImageFont.truetype(name,size)
def person(d,cx,cy,scale=1,accent=(100,205,210),move=0):
    """Stylized human, deliberate proportions, no external photo asset."""
    S=lambda x: x*scale
    circle(d,cx,cy-S(65),S(30),(246,194,151))
    d.arc((cx-S(32),cy-S(98),cx+S(32),cy-S(37)),180,350,fill=(62,54,57),width=max(2,int(S(8))))
    box(d,(cx-S(44),cy-S(30),cx+S(44),cy+S(81)),accent,rounding=max(3,int(S(18))))
    d.line((cx-S(43),cy,cx-S(78),cy+S(38)+move),fill=(246,194,151),width=max(3,int(S(16))))
    d.line((cx+S(43),cy,cx+S(77),cy+S(33)-move),fill=(246,194,151),width=max(3,int(S(16))))
    d.line((cx-S(19),cy+S(72),cx-S(26),cy+S(143)),fill=(107,130,166),width=max(3,int(S(21))))
    d.line((cx+S(20),cy+S(72),cx+S(27),cy+S(143)),fill=(107,130,166),width=max(3,int(S(21))))
def document(d,x,y,accent,highlight=0):
    box(d,(x,y,x+154,y+190),(237,247,251),12)
    d.polygon([(x+118,y),(x+154,y+36),(x+118,y+36)],fill=(193,219,230))
    for j in range(4):
        fill=accent if j==highlight else (139,169,183)
        d.rounded_rectangle((x+23,y+52+j*28,x+121-(j%2)*17,y+63+j*28),radius=4,fill=fill)
def truck(d,x,y,t,accent):
    x=x+int(160*ease(t))
    box(d,(x,y,x+230,y+108),accent,10)
    box(d,(x+230,y+32,x+319,y+109),(242,185,106),8)
    d.polygon([(x+250,y+41),(x+284,y+41),(x+307,y+74),(x+250,y+74)],fill=(136,211,229))
    d.rectangle((x,y+106,x+320,y+117),fill=(104,127,147))
    for wheel in [x+65,x+254]:
        circle(d,wheel,y+119,25,(34,41,54),(212,231,240),4)
        circle(d,wheel,y+119,9,(167,184,195))
def package(d,x,y,color,scale=1):
    w=84*scale;h=76*scale
    box(d,(x,y,x+w,y+h),color,8)
    d.line((x+w*.5,y,x+w*.5,y+h),fill=(253,232,185),width=4)
    d.line((x,y+h*.28,x+w,y+h*.28),fill=(253,232,185),width=3)
def arrow(d,start,end,progress,color):
    p=ease(progress);xx=start[0]+(end[0]-start[0])*p; yy=start[1]+(end[1]-start[1])*p
    d.line((start[0],start[1],xx,yy),fill=color,width=7)
    if p>.96:
        d.polygon([(xx,yy),(xx-15,yy-10),(xx-15,yy+10)],fill=color)
def draw(d,spec,stage,t):
    """Storyboard-specific animation inside y=330..900, never covering subtitles."""
    theme=story_for(spec)
    name,kind1,kind2,kind3,accent,contrast,bg=theme
    kind=[kind1,kind2,kind3][stage]
    pulse=0.5+0.5*math.sin(t*3.0)
    white=(238,247,251);muted=(144,176,198)
    # No generic fallback. New kinds must receive a meaningful drawing.
    if kind in ("library","scan","archive","recall","test_set"):
        for k,x in enumerate((95,280,465)):
            off=int(15*math.sin(t*2+k))
            document(d,x,490+off,accent,k%4 if kind!="scan" else (1 if k==1 else 9))
        if kind=="library":
            box(d,(182,794,540,861),(35,66,84),20,accent)
            centered(d,360,812,"SEARCH THE LIBRARY",f(20),white)
        elif kind=="scan":
            x=int(75+480*ease(t/2.3))
            d.rounded_rectangle((x,462,x+80,717),radius=17,outline=contrast,width=5)
            centered(d,360,807,"SELECT RELEVANT PASSAGES",f(19),white)
        elif kind=="test_set":
            centered(d,360,808,"QUESTIONS AND EXPECTED SOURCES",f(18),white)
        else:
            centered(d,360,808,"RETRIEVE WHAT MATTERS",f(19),white)
    elif kind in ("answer","citation_check","score"):
        box(d,(80,421,640,823),(241,248,251),26)
        label(d,(115,454),"ANSWER",f(26),bg)
        for k in range(4):
            d.rounded_rectangle((115,535+k*47,590-k*45,550+k*47),radius=6,fill=(164,185,196))
        for k in range(3):
            if t>k*.35:
                circle(d,136,734+k*31,9,accent)
                label(d,(158,722+k*31),"Source "+str(k+1),f(17,False),bg)
        if kind in ("citation_check","score"):
            circle(d,567,469,32,accent)
            label(d,(549,451),"✓",f(33),bg)
    elif kind in ("ad","keyword","person_search","storefront","shopping_cart","product"):
        if kind=="ad":
            person(d,190,676,.78,accent,move=10*math.sin(t*2))
            box(d,(359,463,630,795),(240,248,251),24)
            centered(d,494,494,"SPONSORED",f(19),bg)
            package(d,442,556,contrast,1.2)
            box(d,(391,721,596,759),accent,11)
            centered(d,494,724,"SHOP NOW",f(20),bg)
        elif kind in ("person_search","keyword"):
            person(d,214,663,.9,contrast,move=6*math.sin(t*3))
            box(d,(333,474,642,586),(248,251,252),27)
            circle(d,375,529,21,(255,255,255),accent,4)
            d.line((391,545,411,567),fill=accent,width=7)
            centered(d,520,511,"SEARCH",f(24),bg)
            arrow(d,(350,629),(585,629),t/1.4,accent)
        elif kind=="product":
            box(d,(180,390,545,839),(240,250,250),25)
            package(d,304,483,contrast,1.4)
            for i in range(3):
                circle(d,254+i*104,741,19,accent)
            centered(d,359,785,"PRODUCT GALLERY",f(21),bg)
        elif kind=="shopping_cart":
            person(d,160,617,.67,contrast,move=12*math.sin(t*3))
            d.line((316,631,568,631),fill=accent,width=6)
            d.line((337,631,358,737),fill=accent,width=7)
            d.line((358,737,539,737),fill=accent,width=7)
            d.line((539,737,560,651),fill=accent,width=7)
            for x in (394,515):circle(d,x,755,19,(37,65,77),(233,242,245),4)
            package(d,396,551,contrast,.85)
            centered(d,365,829,"A REAL CUSTOMER JOURNEY",f(19),white)
        elif kind=="storefront":
            box(d,(148,509,571,822),(240,247,250),12)
            d.polygon([(121,514),(602,514),(561,433),(166,433)],fill=accent)
            for x in (173,272,371,470):d.rectangle((x,507,x+74,564),fill=contrast)
            box(d,(223,626,314,820),(112,187,209),8)
            box(d,(357,626,518,740),(156,207,225),8)
            centered(d,361,759,"YOUR LISTING",f(18),bg)
    elif kind in ("metrics","fees","profit","receipts","coins","timeline","opportunity"):
        panel=(84,448,636,828);box(d,panel,(241,248,250),24)
        centered(d,360,468,"BUSINESS PERFORMANCE",f(20),bg)
        if kind=="timeline":
            d.line((115,680,613,680),fill=(106,152,176),width=6)
            for i in range(5):
                x=155+i*105
                circle(d,x,680,13,accent if i<3 else contrast)
                label(d,(x-12,713),str(i+1),f(18),bg)
            arrow(d,(120,614),(605,614),t/2.0,accent)
        elif kind in ("receipts","fees"):
            for i,txt in enumerate(("SALES","FEES","PROFIT")):
                box(d,(121,540+i*77,591,598+i*77),(225,239,242),11)
                label(d,(145,558+i*77),txt,f(22),bg)
                d.rectangle((334,562+i*77,334+int((195-i*42)*ease(t/2)),583+i*77),fill=accent if i!=1 else contrast)
        else:
            bars=(108,182,144,228)
            for i,hh in enumerate(bars):
                x=132+i*124; h=int(hh*ease(t/2))
                d.rounded_rectangle((x,768-max(4,h),x+66,768),radius=6,fill=accent if i%2==0 else contrast)
            d.line((119,776,614,776),fill=(104,137,152),width=4)
            label(d,(136,795),"Illustrative only",f(15,False),bg)
    elif kind in ("bot","workflow","stopwatch","human_review","shield","attack","prompt"):
        if kind=="human_review":
            person(d,360,636,1.3,contrast,move=7*math.sin(t*2))
            box(d,(81,458,261,546),(43,76,96),17,accent)
            centered(d,171,483,"REVIEW",f(22),white)
            arrow(d,(265,507),(327,507),t/2,accent)
        elif kind in ("bot","workflow","prompt"):
            box(d,(190,461,530,757),(224,239,251),35)
            circle(d,275,551,25,accent);circle(d,446,551,25,accent)
            d.arc((270,548,445,689),0,180,fill=bg,width=8)
            for k in range(4):
                x=208+k*100
                d.line((x,459-20*math.sin(t+k),x,423),fill=contrast,width=4)
            centered(d,360,803,"AUTOMATED DECISIONS",f(21),white)
        elif kind=="stopwatch":
            circle(d,360,620,158,(40,74,96),accent,8)
            d.line((360,620,360,525),fill=contrast,width=11)
            angle=t*1.3
            d.line((360,620,360+110*math.sin(angle),620-110*math.cos(angle)),fill=accent,width=8)
            centered(d,360,814,"TIME AND STEP LIMITS",f(22),white)
        else:
            d.polygon([(360,411),(549,481),(528,684),(360,819),(192,684),(171,481)],fill=(37,83,107),outline=accent)
            centered(d,360,573,"✓" if kind=="shield" else "!",f(113),contrast)
            centered(d,360,838,"CHECK PERMISSIONS",f(22),white)
    elif kind in ("semantic","exact","merge"):
        for i in range(5):
            theta=i*2*math.pi/5+t*.2
            x=360+175*math.cos(theta);y=640+159*math.sin(theta)
            circle(d,x,y,30,accent if i%2 else contrast)
            d.line((360,635,x,y),fill=(103,158,178),width=5)
        circle(d,360,635,70,(38,79,107),contrast,5)
        centered(d,360,619,"AI",f(34),white)
        centered(d,360,850,{"semantic":"MEANING","exact":"EXACT TERMS","merge":"HYBRID RANKING"}[kind],f(21),white)
    elif kind in ("filters",):
        for i,w in enumerate((452,355,254,142)):
            box(d,(135,434+i*105,135+w,508+i*105),accent if i==3 else (42,84,108),15)
            centered(d,365,451+i*105,("MANY TERMS","INTENT FILTER","RELEVANT","ACTION")[i],f(19),white)
    elif kind in ("warehouse","truck"):
        if kind=="warehouse":
            d.polygon([(89,514),(360,378),(631,514)],fill=accent)
            box(d,(113,515,608,838),(51,91,106),10)
            for row in range(2):
                for col in range(4):
                    package(d,155+105*col,588+105*row,contrast if row==0 else accent,.83)
            centered(d,360,864,"INVENTORY IS FINITE",f(21),white)
        else:
            truck(d,64,604,t/2,accent)
            centered(d,360,839,"REPLENISHMENT LEAD TIME",f(21),white)
    else:
        raise RuntimeError("No approved custom scene art for "+kind)

def intro(d,spec,t):
    """Three distinct types of openings: a person, a product/logistics prop or data."""
    idx=(date.fromisoformat(spec["id"][6:])-date(2026,11,27)).days
    accent=story_for(spec)[4]; contrast=story_for(spec)[5]
    if idx%4==0:
        for k in range(3):
            document(d,122+k*175,641+int(13*math.sin(t*2+k)),accent,k)
    elif idx%4==1:
        person(d,218,723,.82,accent,move=8*math.sin(t*2))
        package(d,411,646,contrast,1.3)
    elif idx%4==2:
        person(d,340,690,1.0,contrast,move=12*math.sin(t*2))
        circle(d,558,553,66,(39,79,102),accent,5)
        centered(d,558,530,"?",f(66),accent)
    else:
        for k,hh in enumerate((112,205,139,275)):
            x=137+k*126
            d.rounded_rectangle((x,900-int(hh*ease(t/1.6)),x+74,900),radius=10,fill=accent if k%2 else contrast)
