#!/usr/bin/env bash
# Tạo lại toàn bộ audio cho video Ember Tarot.
#  - Có `multix`: nhạc nền MiniMax + voice-over Gemini 3.8 Flash (tiếng Việt).
#  - Không có `multix`: fallback (gTTS tiếng Việt + nhạc tổng hợp bằng numpy).
# Sau đó: ghép VO theo mốc thời gian (scripts/vo_script.json), tính timing từng từ,
# sinh lại compositions/captions.html.
#
# LƯU Ý: cú pháp các lệnh multix bên dưới là GIẢ ĐỊNH (môi trường dựng video không có multix).
# Hãy đối chiếu với `multix --help` và sửa 3 biến MULTIX_* nếu khác.
set -euo pipefail
cd "$(dirname "$0")/.."

MUSIC_PROMPT="cute mystical TikTok pop, 120 BPM, music box arpeggios, soft dreamy pad, bouncy bass, \
four-on-the-floor kick, sparkly chimes; energetic build, a drop at 0:24, soft calm breakdown from 0:47, \
ends gently at 0:54; instrumental, no vocals"
VOICE_STYLE=$(python3 -c "import json;print(json.load(open('scripts/vo_script.json'))['voice_style'])")

MULTIX_MUSIC_CMD=${MULTIX_MUSIC_CMD:-"multix music generate --model minimax/music --duration 55"}
MULTIX_TTS_CMD=${MULTIX_TTS_CMD:-"multix tts --model gemini-3.8-flash --language vi-VN"}

mkdir -p assets/audio/vo_lines
if command -v multix >/dev/null 2>&1; then
  echo "→ multix: nhạc nền (MiniMax)"
  $MULTIX_MUSIC_CMD --prompt "$MUSIC_PROMPT" --output assets/audio/music.raw.mp3
  ffmpeg -y -loglevel error -i assets/audio/music.raw.mp3 -t 54.5 -af "afade=t=out:st=51.5:d=3,loudnorm=I=-16:TP=-1.5" -ar 44100 -ac 2 assets/audio/music.wav
  echo "→ multix: voice-over (Gemini 3.8 Flash, tiếng Việt)"
  python3 - <<'PY' | while IFS=$'\t' read -r id text; do
import json
for l in json.load(open("scripts/vo_script.json"))["lines"]:
    print(l["id"] + "\t" + l["text"])
PY
    $MULTIX_TTS_CMD --style "$VOICE_STYLE" --text "$text" --output "assets/audio/vo_lines/$id.raw.wav"
    ffmpeg -y -loglevel error -i "assets/audio/vo_lines/$id.raw.wav" \
      -af "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" \
      -ac 1 -ar 44100 "assets/audio/vo_lines/$id.wav"
  done
else
  echo "! Không tìm thấy multix → dùng fallback"
  pip install -q gTTS numpy >/dev/null 2>&1 || true
  python3 scripts/tts_fallback.py "${TMPDIR:-/tmp}"
  python3 scripts/make_music.py
fi

python3 scripts/build_vo.py        # -> assets/audio/vo.wav + scripts/words.json
python3 scripts/build_captions.py  # -> compositions/captions.html
echo "✓ Xong. Nếu câu nào dài/ngắn hơn, chỉnh 'start' trong scripts/vo_script.json rồi chạy lại."
