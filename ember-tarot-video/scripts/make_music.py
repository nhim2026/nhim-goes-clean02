"""Fallback music bed (used only when multix/MiniMax music is unavailable).
120 BPM, cute-mystic pluck pop: music-box arps, soft pad, bouncy bass, 4-on-floor.
Drop at 24.0 s (shuffle), breakdown at 47.0 s (CTA). Also writes card SFX."""
import numpy as np, wave, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR=44100; BPM=120; B=60/BPM; TOTAL=54.5; N=int(TOTAL*SR)
rng=np.random.default_rng(7)
def write(path,x,stereo=None):
    x=np.asarray(x,np.float32)
    if x.ndim==1: x=np.stack([x,x],1)
    pk=np.max(np.abs(x)); x=x*(0.89/pk) if pk>0 else x
    with wave.open(path,"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes())
def fft_filter(x,lo=None,hi=None):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/SR); g=np.ones_like(f)
    if hi: g*=1/np.sqrt(1+(f/hi)**4)
    if lo: g*=1/np.sqrt(1+(lo/np.maximum(f,1e-3))**4)
    return np.fft.irfft(X*g,len(x))
def midi(m): return 440*2**((m-69)/12)
def env(n,a,d):
    t=np.arange(n)/SR; e=np.exp(-t/d); ka=int(a*SR)
    if ka>0: e[:ka]*=np.linspace(0,1,ka)
    return e
def add(buf,x,t,g=1.0):
    i=int(round(t*SR));
    if i>=len(buf): return
    j=min(len(buf),i+len(x)); buf[i:j]+=x[:j-i]*g
L=np.zeros(N); R=np.zeros(N)
kick=np.zeros(N); clap=np.zeros(N); hat=np.zeros(N); bass=np.zeros(N); pad=np.zeros(N); box=np.zeros(N); boxR=np.zeros(N)
# chords (bar = 4 beats = 2 s): Fmaj7, G6, Em7, Am9
prog=[[53,57,60,64],[55,59,62,64],[52,55,59,62],[57,60,64,71]]
roots=[41,43,40,45]
def section(t):
    if t<4: return "hook"
    if t<23.5: return "groove"
    if t<24: return "fill"
    if t<31: return "drop"
    if t<46.5: return "groove"
    if t<47: return "sweep"
    return "outro"
# drums
kt=np.arange(int(0.35*SR))/SR
kick_s=np.sin(2*np.pi*np.cumsum(45+90*np.exp(-kt/0.035))/SR)*np.exp(-kt/0.16)
kick_s+=0.25*rng.standard_normal(len(kt))*np.exp(-kt/0.004)
cl=rng.standard_normal(int(0.25*SR)); cl=fft_filter(cl,900,4000)
ce=np.zeros(len(cl));
for o in [0,0.011,0.022]: ce+=np.roll(env(len(cl),0.001,0.012 if o<0.02 else 0.09),int(o*SR))
clap_s=cl*ce
hh=fft_filter(rng.standard_normal(int(0.12*SR)),7000,None); hat_c=hh*env(len(hh),0.001,0.022); hat_o=hh*env(len(hh),0.001,0.07)
nbeats=int(TOTAL/B)
for b in range(nbeats):
    t=b*B; s=section(t); beat=b%4
    if s in("hook","groove","drop","fill","sweep") or (s=="outro" and t<50):
        add(kick,kick_s,t,1.0 if s!="outro" else 0.55)
    if s in("groove","drop","hook") and beat in(1,3): add(clap,clap_s,t,0.8)
    if s in("groove","drop","hook","sweep"):
        add(hat,hat_c,t+B/2+0.012,0.5); add(hat,hat_c,t,0.22)
        if s=="drop":
            add(hat,hat_c,t+B/4,0.25); add(hat,hat_o,t+3*B/4,0.3)
    if s=="fill":
        for k in range(8): add(clap,clap_s,t+k*B/8,0.35+0.08*k)
# bass
for b in range(nbeats):
    t=b*B; s=section(t)
    if s in("outro","fill") : continue
    bar=int(t/(4*B))%4; beat=b%4
    for off,dur in ([(0,0.35),(0.75,0.2)] if beat in(0,2) else [(0.5,0.2)]):
        n=int((dur+0.1)*SR); tt=np.arange(n)/SR; f=midi(roots[bar]+(12 if (s=="drop" and off==0.5) else 0))
        x=(np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*2*f*tt)+0.12*np.sign(np.sin(2*np.pi*f*tt)))*env(n,0.004,dur*0.7)
        add(bass,x,t+off*B,0.55 if s!="drop" else 0.7)
# pad: detuned saws, filtered, per bar
for bi in range(int(TOTAL/(4*B))+1):
    t=bi*4*B; n=int(4*B*SR)+int(0.4*SR); tt=np.arange(n)/SR; ch=prog[bi%4]; x=np.zeros(n)
    for m in ch:
        for d in (-0.08,0.08):
            f=midi(m+12)*2**(d/12); x+=2*((tt*f)%1)-1
    e=np.minimum(1,tt/0.25)*np.minimum(1,np.maximum(0,(n/SR-tt)/0.4))
    add(pad,x*e/8,t)
pad=fft_filter(pad,180,1800)
# music box arps (bell: partials 1, 2.76, 5.4) with ping-pong echo
def bell(f,dur=0.9):
    n=int(dur*SR); tt=np.arange(n)/SR
    return (np.sin(2*np.pi*f*tt)*np.exp(-tt/0.45)+0.35*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt/0.12)+0.12*np.sin(2*np.pi*5.4*f*tt)*np.exp(-tt/0.05))*env(n,0.002,10)
pat=[0,2,1,3,2,1,3,0]
for k in range(int(TOTAL/(B/2))):
    t=k*B/2; s=section(t); bar=int(t/(4*B))%4
    if s=="outro" and k%2: continue
    if s=="fill": continue
    ch=prog[bar]; m=ch[pat[k%8]]+24
    if s=="drop" and k%8 in(3,7): m+=7
    g=0.32 if s!="outro" else 0.4
    add(box,bell(midi(m)),t,g)
    add(boxR,bell(midi(m)),t+0.375,g*0.45); add(box,bell(midi(m)),t+0.75,g*0.2)
# riser into drop (filtered noise up-sweep) + sweep into outro
def sweep(dur,up=True):
    n=int(dur*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=int(0.05*SR)
    for i in range(0,n,seg):
        p=i/n if up else 1-i/n; hi=400+9000*p**2
        out[i:i+seg]=fft_filter(x[i:i+seg],hi*0.5,hi)[:len(out[i:i+seg])]
    return out*(np.linspace(0,1,n)**2 if up else np.linspace(1,0,n))
add(hat,sweep(2.0),22.0,0.5); add(hat,sweep(1.0,False),46.6,0.35)
# sidechain pump from the kick grid
duck=np.ones(N)
for b in range(nbeats):
    t=b*B
    if section(t) in("outro","fill"): continue
    i=int(t*SR); n=int(0.32*SR); j=min(N,i+n); duck[i:j]=np.minimum(duck[i:j],1-0.55*np.exp(-np.arange(j-i)/SR/0.09))
# master
tt=np.arange(N)/SR
fade=np.minimum(1,np.maximum(0,(TOTAL-tt)/3.0))
mono=kick*0.9+clap*0.45+bass*duck+pad*0.9*duck
L=(mono+hat*0.35*1.1+box*1.0+boxR*0.6)*fade
R=(mono+hat*0.35*0.9+box*0.6+boxR*1.0)*fade
L=np.tanh(L*1.1); R=np.tanh(R*1.1)
write(f"{root}/assets/audio/music.wav",np.stack([L,R],1))
# ---- SFX ----
sfx=f"{root}/assets/sfx"
def flip():
    n=int(0.16*SR); x=rng.standard_normal(n); out=np.zeros(n); seg=int(0.008*SR)
    for i in range(0,n,seg):
        p=i/n; c=1500+5000*p
        out[i:i+seg]=fft_filter(x[i:i+seg+64],c*0.6,c*1.4)[:len(out[i:i+seg])]
    out*=np.sin(np.pi*np.minimum(1,np.arange(n)/n))**1.5
    tap=fft_filter(rng.standard_normal(int(0.03*SR)),300,2500)*env(int(0.03*SR),0.0005,0.006)
    y=np.zeros(int(0.2*SR)); y[:n]+=out; y[int(0.135*SR):int(0.135*SR)+len(tap)]+=tap*2.2
    return y
write(f"{sfx}/card-flip.wav",flip())
def riffle(dur=1.1,count=34):
    n=int(dur*SR); y=np.zeros(n)
    for k in range(count):
        p=k/count; t=dur*(p**0.8)*0.92
        c=fft_filter(rng.standard_normal(int(0.012*SR)),1800,7000)*env(int(0.012*SR),0.0003,0.003)
        add(y,c,t,0.6+0.4*rng.random())
    tail=fft_filter(rng.standard_normal(int(0.15*SR)),400,3000)*env(int(0.15*SR),0.002,0.03)
    add(y,tail,dur*0.92,1.4); return y
write(f"{sfx}/shuffle-riffle.wav",riffle())
def deal():
    n=int(0.14*SR); x=fft_filter(rng.standard_normal(n),800,5000); e=np.sin(np.pi*np.arange(n)/n)**2
    return x*e
write(f"{sfx}/card-deal.wav",deal())
print("ok")
