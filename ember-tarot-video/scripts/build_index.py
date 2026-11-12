"""Writes index.html: scene hosts, captions host, VO, music and SFX placements."""
import os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOTAL = 54.5
scenes = [("hook",0,4.0),("home",4.0,3.5),("spreads",7.5,7.5),("decks",15.0,5.0),("ask",20.0,4.0),
          ("shuffle",24.0,7.0),("meanings",31.0,5.0),("reading",36.0,3.5),("keeper",39.5,3.5),
          ("history",43.0,4.0),("cta",47.0,7.5)]
# (file, start, volume, duration or None)
sfx = [("sparkle.mp3",0.05,0.5,None),("card-flip.wav",0.62,0.9,None),("card-flip.wav",0.98,0.8,None),("card-flip.wav",1.34,0.9,None),
       ("pop.mp3",2.15,0.6,None),("whoosh.mp3",3.55,0.6,None),
       ("click-soft.mp3",5.62,0.9,None),("whoosh-short.mp3",7.12,0.6,None),
       ("pop.mp3",7.9,0.5,None),("pop.mp3",9.62,0.4,None),("pop.mp3",10.4,0.4,None),("pop.mp3",11.16,0.4,None),
       ("pop.mp3",11.85,0.4,None),("pop.mp3",12.6,0.4,None),("pop.mp3",13.68,0.45,None),
       ("whoosh-short.mp3",14.92,0.55,None),("card-flip.wav",16.52,0.9,None),("whoosh.mp3",17.78,0.5,None),
       ("card-flip.wav",18.45,0.9,None),("sparkle.mp3",18.9,0.45,None),
       ("pop.mp3",20.45,0.45,None),("click-soft.mp3",23.45,0.9,None),("whoosh-cinematic.mp3",23.6,0.45,2.2),
       ("shuffle-riffle.wav",24.3,0.9,None),("shuffle-riffle.wav",24.95,0.8,None),("whoosh-short.mp3",25.85,0.6,None),
       ("card-deal.wav",26.2,0.9,None),("card-deal.wav",26.45,0.9,None),("card-deal.wav",26.7,0.9,None),
       ("card-flip.wav",27.1,1.0,None),("card-flip.wav",27.42,1.0,None),("card-flip.wav",27.74,1.0,None),
       ("sparkle.mp3",27.2,0.5,None),("chime.mp3",28.55,0.45,None),("whoosh.mp3",30.75,0.55,None),
       ("pop.mp3",31.3,0.4,None),("card-flip.wav",33.9,0.9,None),("whoosh-short.mp3",34.8,0.5,None),
       ("whoosh-short.mp3",35.8,0.5,None),("pop.mp3",36.3,0.45,None),("click-soft.mp3",37.55,0.9,None),
       ("whoosh-short.mp3",39.3,0.5,None),("pop.mp3",40.05,0.45,None),("pop.mp3",41.55,0.45,None),
       ("whoosh-short.mp3",42.85,0.5,None),("pop.mp3",43.75,0.35,None),("pop.mp3",43.95,0.35,None),("pop.mp3",44.15,0.35,None),
       ("riser.mp3",44.13,0.4,3.5),("impact-bass-1.mp3",47.55,0.7,None),("pop.mp3",48.55,0.5,None),
       ("card-flip.wav",50.25,0.8,None),("chime.mp3",50.4,0.4,None),("sparkle.mp3",50.5,0.4,None)]
hosts = "\n".join(
  f'      <div id="{n}" data-composition-id="{n}" data-composition-src="compositions/{n}.html" class="clip" data-start="{s}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:{i+1}"></div>'
  for i,(n,s,d) in enumerate(scenes))
import subprocess as _sp
def _dur(f):
    return float(_sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{root}/assets/sfx/{f}"],capture_output=True,text=True).stdout)
lanes=[]; placed=[]
for (f,st,v,d) in sfx:
    d = d or round(_dur(f),3)
    for li,end in enumerate(lanes):
        if end <= st: lanes[li]=st+d; break
    else:
        lanes.append(st+d); li=len(lanes)-1
    placed.append((f,st,v,d,li))
sfx_tags = "\n".join(
  f'      <audio id="sfx{i}" class="clip" src="assets/sfx/{f}" data-start="{st}" data-duration="{d}" data-track-index="{10+li}" data-volume="{v}"></audio>'
  for i,(f,st,v,d,li) in enumerate(placed))
_unused = "\n".join(
  f'      <audio id="sfx{i}" class="clip" src="assets/sfx/{f}" data-start="{s}"{(f" data-duration=\"{d}\" data-fade-out=\"0.4\"" if d else "")} data-track-index="{4+i%3}" data-volume="{v}"></audio>'
  for i,(f,s,v,d) in enumerate(sfx))
html = f'''<!doctype html>
<html lang="vi" data-composition-variables='[{{"id":"rating","type":"string","label":"Rating","default":"4.8"}}]'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <script src="assets/fx.js"></script>
    <link rel="stylesheet" href="assets/ember.css" />
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #f6efdf; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; font-family: "Nunito", sans-serif; }}
      #ground {{ position: absolute; inset: 0; background: #f6efdf; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="ground"></div>
{hosts}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:50"></div>
      <audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-track-index="3" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/audio/music.wav" data-start="0" data-track-index="7" data-volume="0.22" data-fade-out="2"></audio>
{sfx_tags}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f"{root}/index.html","w").write(html)
print("index.html written", len(sfx), "sfx")
