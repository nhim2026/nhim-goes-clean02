import os, subprocess, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
REC = f"{S}/rec3/r1_blur.mp4"
KIT = f"{S}/kit"
OUT = f"{S}/t6"
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
INK = (32, 53, 68); CYAN = (102, 193, 213); PINK = (233, 157, 181); PAPER = (247, 249, 252)
FB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FM = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
EMO = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMO_RE = re.compile("([\U0001F300-\U0001FAFF☀-➿️‍]+)")

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode: raise SystemExit(cmd + "\n" + r.stderr[-2000:])

def text_runs(line, size, font):
    """Render one line mixing Inter text and Noto emoji; returns RGBA image."""
    f = ImageFont.truetype(font, size)
    ef = ImageFont.truetype(EMO, 109)
    parts = [p for p in EMO_RE.split(line) if p]
    imgs = []
    for p in parts:
        if EMO_RE.fullmatch(p):
            p = p.replace("️", "")
            for ch in p:
                if ch == "‍": continue
                im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((0, 0), ch, font=ef, embedded_color=True)
                im = im.crop(im.getbbox()).resize((int(size * 1.05), int(size * 1.05)), Image.LANCZOS)
                imgs.append((im, True))
        else:
            bb = f.getbbox(p)
            im = Image.new("RGBA", (bb[2] + 4, int(size * 1.3)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((0, int(size * 0.05)), p, font=f, fill=INK)
            imgs.append((im, False))
    w = sum(i.width for i, _ in imgs) + 6 * (len(imgs) - 1)
    h = int(size * 1.3)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
    for im, e in imgs:
        out.paste(im, (x, (h - im.height) // 2 if e else 0), im); x += im.width + 6
    return out

def banner(lines, name, y=250, size=60, sub=None):
    """White rounded card, ink text, cyan->pink accent bar. Full-frame RGBA png."""
    rendered = [text_runs(l, size, FB) for l in lines]
    if sub: rendered.append(text_runs(sub, int(size * 0.62), FM))
    tw = max(r.width for r in rendered); th = sum(r.height for r in rendered)
    pw, ph = 48, 34
    cw, ch = min(tw + 2 * pw, W - 80), th + 2 * ph
    fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0 = (W - cw) // 2
    ImageDraw.Draw(sh).rounded_rectangle([x0, y + 12, x0 + cw, y + ch + 12], 40, fill=(32, 53, 68, 70))
    fr = Image.alpha_composite(fr, sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([x0, y, x0 + cw, y + ch], 40, fill=PAPER + (245,))
    # gradient accent bar on top edge
    bar = Image.new("RGBA", (cw - 80, 10))
    for i in range(bar.width):
        t = i / bar.width
        bar.putpixel((i, 0), tuple(int(CYAN[k] * (1 - t) + PINK[k] * t) for k in range(3)) + (255,))
    bar = bar.resize((cw - 80, 10)); bar = Image.new("RGBA", bar.size)  # placeholder replaced below
    g = Image.linear_gradient("L").rotate(90).resize((cw - 80, 10))
    col = Image.composite(Image.new("RGBA", g.size, PINK + (255,)), Image.new("RGBA", g.size, CYAN + (255,)), g)
    m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, g.size[0] - 1, 9], 5, fill=255)
    fr.paste(col, (x0 + 40, y - 5), m)
    cy = y + ph
    for r in rendered:
        fr.paste(r, ((W - r.width) // 2, cy), r); cy += r.height
    fr.save(f"{OUT}/{name}.png")
    return f"{OUT}/{name}.png"

def still(t, name, crop_y, crop_h, marks):
    """Freeze source frame at t, crop a band (full width), scale to 1080 wide, place on paper bg,
    draw highlighter marks (source-pixel y ranges)."""
    run(f'ffmpeg -v error -y -ss {t} -i "{REC}" -frames:v 1 {OUT}/{name}_raw.png')
    im = Image.open(f"{OUT}/{name}_raw.png").convert("RGBA")
    hl = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(hl)
    for (x1, y1, x2, y2), c in marks:
        d.rounded_rectangle([x1, y1, x2, y2], 18, fill=c + (90,), outline=c + (255,), width=7)
    im = Image.alpha_composite(im, hl)
    band = im.crop((0, crop_y, im.width, crop_y + crop_h))
    s = 1080 / band.width * 1.0
    band = band.resize((1080, int(band.height * s)), Image.LANCZOS)
    bg = Image.open(f"{KIT}/brand/brand/social/ember-social-story-light-1080x1920-blank.jpg").convert("RGBA").resize((W, H))
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    y = (H - band.height) // 2 + 60
    m = Image.new("L", band.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, band.width - 1, band.height - 1], 36, fill=255)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, y + 16, W - 20, y + band.height + 16], 40, fill=(32, 53, 68, 80))
    bg = Image.alpha_composite(bg, sh.filter(ImageFilter.GaussianBlur(22)))
    bg.paste(band, (0, y), m)
    bg.convert("RGB").save(f"{OUT}/{name}.png")
    return f"{OUT}/{name}.png"

segs = []  # (file, duration, sfx list [(offset, kind)])

def seg_clip(name, src, ss, dur, ban, sfx=()):
    run(f'ffmpeg -v error -y -ss {ss} -t {dur} -i "{src}" -i {ban} -filter_complex '
        f'"[0:v]scale={W}:{H},fps={FPS},setsar=1[v];[v][1:v]overlay=0:0:enable=\'gte(t,0.15)\'" '
        f'-an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p {OUT}/{name}.mp4')
    segs.append((f"{OUT}/{name}.mp4", dur, list(sfx)))

def seg_rec(name, ss, src_dur, speed, ban, crop_y=426, sfx=()):
    dur = round(src_dur / speed, 3)
    run(f'ffmpeg -v error -y -ss {ss} -t {src_dur} -i "{REC}" -i {ban} -filter_complex '
        f'"[0:v]setpts=PTS/{speed},fps={FPS},scale={W}:-2,crop={W}:{H}:0:{crop_y},setsar=1[v];[v][1:v]overlay=0:0" '
        f'-an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -t {dur} {OUT}/{name}.mp4')
    segs.append((f"{OUT}/{name}.mp4", dur, list(sfx)))

def seg_still(name, png, dur, ban, sfx=()):
    # gentle push-in 1.00 -> 1.04
    run(f'ffmpeg -v error -y -loop 1 -t {dur} -i {png} -i {ban} -filter_complex '
        f'"[0:v]fps={FPS},scale=w=\'{W}*(1+0.04*t/{dur})\':h=-2:eval=frame,crop={W}:{H},setsar=1[v];[v][1:v]overlay=0:0:enable=\'gte(t,0.2)\'" '
        f'-an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p {OUT}/{name}.mp4')
    segs.append((f"{OUT}/{name}.mp4", dur, list(sfx)))

HOOK = f"{KIT}/hook.mp4"; TWIST = f"{KIT}/twist.mp4"

# 1-2. Bé Em hook
seg_clip("s01", HOOK, 0, 4.2, banner(["Quên sinh nhật bạn thân", "lần thứ 3 trong năm 💀"], "b01", y=230, size=66), [(0.15, "pop")])
seg_clip("s02", HOOK, 4.2, 2.3, banner(["Đừng hỏi bạn,", "hỏi Keeper nè! 🔥"], "b02", y=230, size=66), [(0.15, "pop")])
# 3-4. typing + answer
seg_rec("s03", 2.0, 8.5, 2.5, banner(["“Sắp đến sinh nhật ai hông bà?”"], "b03", y=230, size=52), sfx=[(0.0, "whoosh"), (0.15, "pop")])
seg_rec("s04", 10.5, 13.6, 3.0, banner(["Keeper check giùm liền ⚡"], "b04", y=230, size=56), sfx=[(0.15, "pop")])
# 5. zoom on answer #1
p = still(24.2, "z1", 1380, 760, [((25, 1548, 1295, 1802), CYAN)])
seg_still("s05", p, 2.8, banner(["30 ngày tới không ai", "sinh nhật hết 😮‍💨"], "b05", y=230, size=60), sfx=[(0.0, "whoosh"), (0.3, "ding")])
# 6-7. ask about Tí
seg_rec("s06", 26.5, 18.5, 4.4, banner(["“Vậy khi nào sinh nhật em trai,", "nên mua quà gì?”"], "b06", y=230, size=52), sfx=[(0.0, "whoosh"), (0.15, "pop")])
seg_rec("s07", 45.0, 12.0, 2.6, banner(["Keeper lục hồ sơ người thân 🔎"], "b07", y=230, size=52), sfx=[(0.15, "pop")])
# 8. zoom on answer #2
p = still(58.2, "z2", 1640, 700, [((25, 1695, 1295, 1835), CYAN), ((25, 1855, 1295, 1995), PINK), ((25, 2062, 1295, 2202), PINK)])
seg_still("s08", p, 4.6, banner(["Nhớ cả size giày", "lẫn sở thích luôn 😳"], "b08", y=230, size=60), sfx=[(0.0, "whoosh"), (0.3, "ding"), (1.4, "ding")])
# 9. thanks
seg_rec("s09", 72.0, 11.0, 2.6, banner(["Nó nhớ hết luôn á 😭"], "b09", y=230, size=62), sfx=[(0.0, "whoosh"), (0.15, "pop")])
# 10. Bé Em twist (point + wink + wave)
seg_clip("s10", TWIST, 4.0, 6.0, banner(["Ember nhớ giùm bạn", "những điều nhỏ của người thân 💙"], "b10", y=230, size=56), [(0.15, "pop"), (3.4, "ding")])

# 11. CTA end card
bg = Image.open(f"{KIT}/brand/brand/social/ember-social-story-light-1080x1920.jpg").convert("RGBA").resize((W, H))
def put(img, y):
    bg.paste(img, ((W - img.width) // 2, y), img)
put(text_runs("Hỏi Keeper:", 54, FM), 1180)
put(text_runs("“Sắp đến sinh nhật ai?” 🎂", 64, FB), 1255)
d = ImageDraw.Draw(bg)
for i, lab in enumerate(["App Store", "Google Play"]):
    x0 = 150 + i * 410; y0 = 1440
    d.rounded_rectangle([x0, y0, x0 + 370, y0 + 110], 55, fill=INK)
    f = ImageFont.truetype(FB, 44); bw = d.textlength(lab, font=f)
    d.text((x0 + (370 - bw) / 2, y0 + 30), lab, font=f, fill=PAPER)
put(text_runs("Tải Ember miễn phí", 50, FB), 1600)
bg.convert("RGB").save(f"{OUT}/cta.png")
run(f'ffmpeg -v error -y -loop 1 -t 3.6 -i {OUT}/cta.png -vf "fps={FPS},fade=in:0:8,setsar=1" -an -c:v libx264 -crf 18 -pix_fmt yuv420p {OUT}/s11.mp4')
segs.append((f"{OUT}/s11.mp4", 3.6, [(0.0, "whoosh"), (0.4, "ding")]))

# concat video
with open(f"{OUT}/list.txt", "w") as fh:
    for f, _, _ in segs: fh.write(f"file '{f}'\n")
run(f"ffmpeg -v error -y -f concat -safe 0 -i {OUT}/list.txt -c copy {OUT}/video.mp4")

# SFX synthesis
sf = {
 "pop": "sine=f=900:d=0.09,afade=out:st=0.02:d=0.07,volume=0.5",
 "ding": "sine=f=1318:d=0.7,afade=out:st=0.05:d=0.65,volume=0.28",
 "whoosh": "anoisesrc=d=0.4:c=pink:a=0.5,bandpass=f=1200:w=900,afade=in:d=0.18,afade=out:st=0.18:d=0.22,volume=0.9",
}
for k, v in sf.items():
    run(f'ffmpeg -v error -y -f lavfi -i "{v}" -ar 44100 -ac 2 {OUT}/sfx_{k}.wav')
events = []; t = 0.0
for f, dur, sfx in segs:
    for off, k in sfx: events.append((t + off, k))
    actual = float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {f}', shell=True))
    t += actual
total = t
inputs = " ".join(f"-i {OUT}/sfx_{k}.wav" for _, k in events)
fl = ";".join(f"[{i}:a]adelay={int(ts*1000)}|{int(ts*1000)}[a{i}]" for i, (ts, _) in enumerate(events))
mix = "".join(f"[a{i}]" for i in range(len(events)))
run(f'ffmpeg -v error -y {inputs} -filter_complex "{fl};{mix}amix=inputs={len(events)}:normalize=0,apad,atrim=0:{total:.3f}[out]" -map "[out]" -ar 44100 {OUT}/sfx.wav')
run(f'ffmpeg -v error -y -i {OUT}/video.mp4 -i {OUT}/sfx.wav -filter_complex \"[1:a]volume=14dB,alimiter=limit=0.7[a]\" -map 0:v -map \"[a]\" -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart {OUT}/BeEm_T6_sinh-nhat.mp4')
print("total", round(total, 2), "events", len(events))
