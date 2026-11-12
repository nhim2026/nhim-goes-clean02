"""Generate compositions/captions.html from scripts/words.json (karaoke, per-word highlight)."""
import json, os, re, html
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = json.load(open(f"{root}/scripts/words.json"))
SKIP = {"hook", "cta", "outro"}           # these lines are already big on screen
MAXW = 4
groups = []
cur = []
for i, w in enumerate(W):
    if w["line"] in SKIP: continue
    if cur and (w["line"] != cur[-1]["line"] or len(cur) >= MAXW or w["start"] - cur[-1]["end"] > 0.15):
        groups.append(cur); cur = []
    cur.append(w)
    if re.search(r"[,.!?:]$", w["text"]) and len(cur) >= 2:
        groups.append(cur); cur = []
if cur: groups.append(cur)
# merge single-word groups into the previous group of the same line when it has room
merged = []
for g in groups:
    if len(g) == 1 and merged and merged[-1][-1]["line"] == g[0]["line"] and len(merged[-1]) < MAXW + 1:
        merged[-1] += g
    else: merged.append(g)
groups = merged
markup, js = [], []
for gi, g in enumerate(groups):
    s = max(0.05, g[0]["start"] - 0.08)
    nxt = groups[gi + 1][0]["start"] - 0.08 if gi + 1 < len(groups) else 999
    e = min(nxt, g[-1]["end"] + 0.4)
    words = "".join(f'<span class="w" id="cw{w["id"][1:]}">{html.escape(w["text"])}</span>' for w in g)
    markup.append(f'    <div id="cg{gi}" class="clip cg" data-start="{s:.3f}" data-duration="{e - s:.3f}"><div class="pill" id="cp{gi}">{words}</div></div>')
    js.append({"g": gi, "s": round(s, 3), "e": round(e, 3), "w": [[f'cw{w["id"][1:]}', w["start"], w["end"]] for w in g]})
out = f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #root .cg {{ position: absolute; left: 0; top: 1150px; width: 1080px; height: 170px; display: flex; justify-content: center; align-items: center; overflow: visible; }}
    #root .pill {{ display: inline-flex; flex-wrap: nowrap; gap: 24px; padding: 18px 38px 22px; border-radius: 44px; background: rgba(24, 33, 58, 0.92);
      box-shadow: 0 10px 0 rgba(24, 33, 58, 0.18), 0 0 0 4px rgba(232, 194, 122, 0.55); font-family: "Nunito", sans-serif; font-weight: 900; font-size: 60px; line-height: 1.1; white-space: nowrap; }}
    #root .w {{ display: inline-block; color: rgba(246, 239, 223, 0.55); }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920" data-layout-allow-overlap>
{chr(10).join(markup)}
  </div>
  <script>
    (function () {{
      const G = {json.dumps(js, ensure_ascii=False)};
      const tl = gsap.timeline({{ paused: true }});
      G.forEach((g) => {{
        const pill = "#cp" + g.g;
        tl.fromTo(pill, {{ scale: 0.7, opacity: 0, y: 20 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.22, ease: "back.out(2.2)" }}, g.s);
        g.w.forEach(([id, s, e]) => {{
          tl.fromTo("#" + id, {{ color: "rgba(246,239,223,0.55)", scale: 1, y: 0 }}, {{ color: "#E8C27A", scale: 1.1, y: -6, duration: 0.08, ease: "power2.out" }}, s);
          tl.to("#" + id, {{ color: "#F6EFDF", scale: 1, y: 0, duration: 0.12, ease: "power2.out" }}, Math.max(s + 0.09, e));
        }});
        tl.to(pill, {{ opacity: 0, scale: 0.92, duration: 0.1, ease: "power2.in" }}, g.e - 0.1);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
'''
open(f"{root}/compositions/captions.html", "w").write(out)
for g in groups: print(" ".join(w["text"] for w in g))
