"""Auto-blur personal info in an app screen recording.

OCR (Tesseract vie) samples the video every STEP seconds inside the given time
ranges, matches words against sensitive rules, and blurs those boxes (padded,
merged with neighbouring samples so nothing flickers) on every frame.

usage: python3 blur_rec.py SRC OUT RULES.json start-end [start-end ...]
RULES.json: {"words": [...], "regex": [...], "boxes": [[t0,t1,x1,y1,x2,y2], ...]}
Writes OUT (same fps/size as SRC, only the given ranges, concatenated? no:
the full timeline is kept; frames outside ranges are copied untouched).
Also writes OUT + ".boxes.json" for inspection.
"""
import sys, json, re, os, subprocess, unicodedata
from concurrent.futures import ProcessPoolExecutor
import numpy as np, cv2, pytesseract

os.environ["OMP_THREAD_LIMIT"] = "1"
STEP = 0.2       # OCR sample interval (s)
SCALE = 0.5      # OCR on half-size frames
PAD = 14         # px padding in source pixels
SPREAD = 2       # union boxes from +-SPREAD samples

def norm(w):
    w = unicodedata.normalize("NFC", w).strip().strip(".,:;!?()\"“”'")
    return w.lower()

def ocr_at(args):
    src, t, rules = args
    cap = cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read(); cap.release()
    if not ok: return t, []
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
    d = pytesseract.image_to_data(g, lang="vie", output_type=pytesseract.Output.DICT)
    words = {norm(w) for w in rules.get("words", [])}
    regs = [re.compile(r, re.I) for r in rules.get("regex", [])]
    boxes = []
    for i, w in enumerate(d["text"]):
        if not w.strip(): continue
        n = norm(w)
        if n in words or any(r.search(w) for r in regs):
            x, y, ww, hh = (int(v / SCALE) for v in (d["left"][i], d["top"][i], d["width"][i], d["height"][i]))
            boxes.append([x - PAD, y - PAD, x + ww + PAD, y + hh + PAD])
    return t, boxes

def main():
    src, out, rules_p = sys.argv[1:4]
    ranges = [tuple(map(float, r.split("-"))) for r in sys.argv[4:]]
    rules = json.load(open(rules_p))
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); H = int(cap.get(4))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
    ts = sorted({round(a + k * STEP, 3) for a, b in ranges for k in range(int((b - a) / STEP) + 1)})
    with ProcessPoolExecutor(4) as ex:
        res = dict(ex.map(ocr_at, [(src, t, rules) for t in ts], chunksize=4))
    json.dump({str(k): v for k, v in res.items()}, open(out + ".boxes.json", "w"))
    keys = sorted(res)
    def boxes_for(t):
        if not any(a - 0.3 <= t <= b + 0.3 for a, b in ranges): return []
        i = min(range(len(keys)), key=lambda j: abs(keys[j] - t))
        bx = []
        for j in range(max(0, i - SPREAD), min(len(keys), i + SPREAD + 1)):
            bx += res[keys[j]]
        bx += [b[2:] for b in rules.get("boxes", []) if b[0] <= t <= b[1]]
        return bx
    enc = subprocess.Popen(
        f'ffmpeg -v error -y -f rawvideo -pix_fmt bgr24 -s {W}x{H} -r {fps} -i - '
        f'-c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p "{out}"', shell=True, stdin=subprocess.PIPE)
    cap = cv2.VideoCapture(src)
    for f in range(n):
        ok, fr = cap.read()
        if not ok: break
        for x1, y1, x2, y2 in boxes_for(f / fps):
            x1, y1 = max(0, int(x1)), max(0, int(y1)); x2, y2 = min(W, int(x2)), min(H, int(y2))
            if x2 - x1 < 4 or y2 - y1 < 4: continue
            roi = fr[y1:y2, x1:x2]
            small = cv2.resize(roi, (max(1, (x2 - x1) // 14), max(1, (y2 - y1) // 14)), interpolation=cv2.INTER_AREA)
            fr[y1:y2, x1:x2] = cv2.GaussianBlur(cv2.resize(small, (x2 - x1, y2 - y1), interpolation=cv2.INTER_LINEAR), (0, 0), 6)
        enc.stdin.write(fr.tobytes())
    enc.stdin.close(); enc.wait(); cap.release()
    print("samples", len(ts), "hits", sum(1 for v in res.values() if v))

if __name__ == "__main__":
    main()
