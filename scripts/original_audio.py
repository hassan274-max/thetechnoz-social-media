#!/usr/bin/env python3
"""Original 4.8-second electronic sonic logo for TheTechnoz Solutions.
Synthesized from mathematical waveforms: no external samples or recordings.
"""
import argparse
import math
import random
import struct
import wave

RATE=32000
DURATION=4.8
TAU=2*math.pi

def frequency(midi):
    return 440.0 * 2 ** ((midi-69)/12)

def envelope(t, duration, attack=.04, release=.28):
    return min(1.0, t/max(.001,attack), max(0.0,(duration-t)/max(.001,release)))

def add_note(samples, midi, start, duration, amplitude=.08, sound="bell"):
    start_index=int(start*RATE)
    freq=frequency(midi)
    limit=min(len(samples),start_index+int(duration*RATE))
    for i in range(start_index,limit):
        age=(i-start_index)/RATE
        e=envelope(age,duration,attack=.018 if sound=="bell" else .18,release=.30)
        phase=TAU*freq*age
        if sound=="bell":
            timbre=(.83*math.sin(phase) + .14*math.sin(2*phase) +
                    .03*math.sin(3.01*phase))
            e*=math.exp(-.55*age)
        elif sound=="bass":
            timbre=.90*math.sin(phase)+.10*math.sin(2*phase)
        else: # airy soft pad
            timbre=(.68*math.sin(phase) + .20*math.sin(2.003*phase) +
                    .12*math.sin(phase*.501))
        samples[i]+=amplitude*e*timbre

def add_pulse(samples, start, amplitude=.07):
    n0=int(start*RATE)
    for j in range(int(.24*RATE)):
        i=n0+j
        if i>=len(samples):break
        t=j/RATE
        # Original gentle electronic thump with pitch drop
        phase=TAU*(92*t-32*t*t)
        samples[i]+=amplitude*math.exp(-22*t)*math.sin(phase)

def add_shimmer(samples, start, amplitude=.018):
    rng=random.Random(993+int(start*100))
    n0=int(start*RATE)
    for j in range(int(.11*RATE)):
        i=n0+j
        if i>=len(samples):break
        t=j/RATE
        samples[i]+=amplitude*math.exp(-48*t)*(rng.random()*2-1)

def build(path):
    n=int(RATE*DURATION)
    audio=[0.0]*n
    # Two warm original harmonies, with soft transition.
    for start,notes in [(0.0,(57,60,64,71)),(2.4,(53,57,60,67))]:
        for note in notes:
            add_note(audio,note,start,2.35,.022,"pad")
    # Subtle bass foundation.
    add_note(audio,45,.0,2.3,.045,"bass")
    add_note(audio,41,2.4,2.3,.043,"bass")
    # Original brief sonic-signature motif.
    for midi,start,dur,amp in [
       (76,.25,.62,.085), (79,1.04,.66,.081),
       (81,1.79,.72,.075), (84,2.76,.66,.08),
       (81,3.64,.88,.073)]:
        add_note(audio,midi,start,dur,amp,"bell")
    for t in (0.0,1.2,2.4,3.6):
        add_pulse(audio,t,.060)
        add_shimmer(audio,t+.58,.012)
    # Master fade and soft limiter, leaving room for phone speakers.
    peak=max(1e-9,max(abs(v) for v in audio))
    gain=min(1.0,.68/peak)
    pcm=bytearray()
    for i,value in enumerate(audio):
        t=i/RATE
        edge=min(1.0,t/.24,(DURATION-t)/.52)
        value=math.tanh(1.1*value*gain)*max(0.0,edge)
        pcm.extend(struct.pack("<h",round(max(-1,min(1,value)) * 32767)))
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(pcm)
    print(f"Created original 4.8-second sound: {path}")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("output")
    build(parser.parse_args().output)
