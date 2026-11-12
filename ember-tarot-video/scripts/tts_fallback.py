"""Fallback VO: Google Translate TTS (vi) per line, sped up and trimmed.
Used only when `multix` (Gemini TTS) is not available. Output: assets/audio/vo_lines/<id>.wav"""
import json, os, subprocess, sys
from gtts import gTTS
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
script = json.load(open(os.path.join(root, "scripts/vo_script.json")))
out = os.path.join(root, "assets/audio/vo_lines"); os.makedirs(out, exist_ok=True)
tmp = sys.argv[1] if len(sys.argv) > 1 else "/tmp"
for ln in script["lines"]:
    mp3 = os.path.join(tmp, ln["id"] + ".mp3")
    gTTS(ln["text"], lang="vi").save(mp3)
    wav = os.path.join(out, ln["id"] + ".wav")
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "atempo=1.28,asetrate=24000*1.04,aresample=44100,atempo=0.9615,"
          "highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", af, "-ac", "1", "-ar", "44100", wav], check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True).stdout.strip()
    print(ln["id"], d)
