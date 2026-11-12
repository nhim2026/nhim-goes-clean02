"""Lay VO lines on the film clock -> assets/audio/vo.wav, and estimate per-word timings
-> scripts/words.json (used to generate compositions/captions.html).
If a real transcript with word timings exists (e.g. from Gemini/multix or whisper),
put it in scripts/words.override.json and it is used instead."""
import json, os, re, subprocess, wave, numpy as np
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(f"{root}/scripts/vo_script.json"))
SR = 44100; TOTAL = 54.5
def load(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-f","s16le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)/32768
def speech_segments(x, thr_db=-34, min_gap=0.09):
    hop = int(0.01*SR); n = len(x)//hop
    rms = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)])
    on = 20*np.log10(rms) > thr_db
    segs=[]; i=0
    while i<n:
        if on[i]:
            j=i
            while j<n and on[j]: j+=1
            segs.append([i*0.01, j*0.01]); i=j
        else: i+=1
    merged=[]
    for s in segs:
        if merged and s[0]-merged[-1][1] < min_gap: merged[-1][1]=s[1]
        else: merged.append(s)
    return merged
def weight(w):
    core = re.sub(r"[^\w]", "", w)
    return 1.2 + 0.18*len(core)
mix = np.zeros(int(TOTAL*SR), np.float32); words=[]
for ln in S["lines"]:
    x = load(f"{root}/assets/audio/vo_lines/{ln['id']}.wav"); D = len(x)/SR
    st = ln["start"]; a = int(st*SR); mix[a:a+len(x)] += x[:len(mix)-a]
    chunks = [c.strip() for c in re.split(r"(?<=[,.!?:])\s+", ln["text"]) if c.strip()]
    segs = speech_segments(x)
    # merge segments down to number of chunks by closing the smallest gaps
    while len(segs) > len(chunks):
        gaps=[segs[i+1][0]-segs[i][1] for i in range(len(segs)-1)]; k=int(np.argmin(gaps))
        segs[k][1]=segs[k+1][1]; del segs[k+1]
    if len(segs) != len(chunks): segs=[[segs[0][0] if segs else 0, D]]; chunks=[ln["text"]]
    for (s0,s1),c in zip(segs,chunks):
        ws=c.split(); W=[weight(w) for w in ws]; tot=sum(W); t=s0
        for w,wt in zip(ws,W):
            d=(s1-s0)*wt/tot
            words.append({"line":ln["id"],"scene":ln["scene"],"text":w,"start":round(st+t,3),"end":round(st+t+d,3)}); t+=d
    print(ln["id"], round(st,2), "->", round(st+D,2), "segs", len(segs))
peak=np.max(np.abs(mix)); mix*= (0.89/peak)
pcm=(mix*32767).astype(np.int16)
with wave.open(f"{root}/assets/audio/vo.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
ov=f"{root}/scripts/words.override.json"
if os.path.exists(ov): words=json.load(open(ov)); print("using override word timings")
for i,w in enumerate(words): w["id"]=f"w{i}"
json.dump(words,open(f"{root}/scripts/words.json","w"),ensure_ascii=False,indent=1)
print(len(words),"words")
