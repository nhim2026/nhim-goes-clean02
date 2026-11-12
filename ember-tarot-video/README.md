# Ember · "Tự xem Tarot" — video motion graphic 9:16

Dự án video viết bằng [HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP, render ra MP4).
1080×1920, 30 fps, 54,5 giây. Bản render: `renders/ember-tarot-9x16.mp4`.

> ⚠️ **Lưu ý khi dựng:** môi trường dựng video **không nhận được file screen recording** và **không có `multix` CLI**
> (cũng không có API key MiniMax/Gemini). Vì vậy:
> - Luồng màn hình bên dưới được dựng lại **theo mô tả trong brief**, không phải từ video gốc. Các nhãn
>   như tên 2 trải bài "Công việc", "Lời khuyên", chữ trên tab bar, lời chào "Chào buổi tối, Nhím"... là **nhãn tạm**:
>   cần đối chiếu với app thật.
> - Logo `assets/art/ember-logo.svg` là **logo tạm**: thay bằng file logo thật (giữ tên file hoặc sửa `compositions/cta.html`).
> - Voice-over hiện là **giọng fallback** (Google TTS tiếng Việt, đã tăng tốc) và nhạc nền là **bản tổng hợp tạm** 120 BPM.
>   Chạy `scripts/generate_audio.sh` trên máy có `multix` để thay bằng MiniMax (nhạc) + Gemini 3.8 Flash (voice).

## 1. Luồng "Tự xem Tarot" (theo brief)

| # | Màn hình | Hành động của người dùng | Điểm cần nhấn mạnh |
|---|---|---|---|
| 1 | Trang chủ | Bấm thẻ **Tự xem Tarot** | Vào thẳng từ Trang chủ, không cần tìm |
| 2 | Chọn trải bài | Chọn 1 trong **8 trải bài** | Một lá, Ba lá, Tình cảm, Nhịp tuần, Gương kết nối, …, Tùy chọn |
| 3 | Chọn bộ bài | Vuốt chọn bộ bài theo vibe | Rider-Waite cổ điển, mặt sau hoa bướm, … |
| 4 | Câu hỏi | Chọn kiểu trải + viết tâm tư/câu hỏi | Cá nhân hóa luận giải |
| 5 | Xáo / rút / lật | Xáo bài, rút bài, lật bài | Nghi thức vui, chỉ việc chờ luận giải |
| 6 | Đang luận giải | Đọc ý nghĩa từng lá trong lúc chờ | Ten of Cups, Judgement… |
| 7 | Luận giải | Đọc + bấm nghe voice | Siêu chi tiết, có voice đọc |
| 8 | Keeper AI | Hỏi tiếp | Giải đáp thêm về trải bài |
| 9 | Lịch sử | Xem lại các lần xem bài | Lưu lại, xem bất cứ lúc nào |

## 2. Storyboard (khớp với `index.html`)

| Thời gian | Scene | Voice-over | Hình ảnh / chuyển động | Âm thanh |
|---|---|---|---|---|
| 0.0–4.0 | `hook` | "Tự xem Tarot, ok hem?" · "Có Ember lo hết nè!" | Nền navy + bụi sao; tiêu đề có sẵn ở frame 0; 3 lá bài nảy lên & lật 3D theo beat; mèo mascot bật lên, vẫy, nháy mắt; iris kem mở từ chú mèo | sparkle, 3× lật bài, pop, whoosh |
| 4.0–7.5 | `home` | "Mở app, bấm Tarot ngay trên Trang chủ." | iPhone trồi lên; mèo chỉ tay; con trỏ "bàn chân mèo" bấm thẻ Tự xem Tarot; sticker "Ngay Trang chủ!"; punch-in, thẻ phóng to thành màn hình kế | click, whoosh |
| 7.5–15.0 | `spreads` | "Tám trải bài cho từng nỗi niềm: một lá, ba lá…" | Sticker "8 trải bài"; lưới 8 trải bài; camera chạy theo, từng thẻ sáng lên **đúng lúc giọng đọc nhắc tên** | pop mỗi thẻ |
| 15.0–20.0 | `decks` | "Chọn bộ bài hợp vibe: Rider Waite cổ điển, hay mặt sau hoa bướm xinh xỉu." | Lá Rider-Waite nhảy khỏi điện thoại & lật (The Lovers); vuốt carousel; lá hoa bướm xoay 360° bay vào | whoosh, lật bài, sparkle |
| 20.0–24.0 | `ask` | "Chọn kiểu trải, rồi gửi gắm tâm tư, câu hỏi của bạn." | Chọn chip "Ba lá"; câu hỏi được gõ từng chữ; mèo suy tư; bấm "Xáo bài thôi!" → zoom xuyên nút vào màn đêm | pop, click, whoosh cinematic |
| 24.0–31.0 | `shuffle` (drop) | "Xáo bài, rút bài, lật bài. Xong! Giờ chỉ cần chờ luận giải." | Riffle chia đôi & đan bài; **văng bài có vật lý** (trọng lực, nảy, ma sát, mô phỏng tất định); thu về; **rải bài** hình quạt; 3 lá bay lên vị trí Quá khứ/Hiện tại/Tương lai; **lật 3D** lần lượt (Ten of Cups, Judgement, The Star); "Xong!" + mèo reo; thanh "Đang luận giải" | riffle ×2, chia bài ×3, lật ×3, chime |
| 31.0–36.0 | `meanings` | "Trong lúc chờ, đọc ý nghĩa từng lá, như Ten of Cups hay Judgement." | Thanh tiến độ chạy; thẻ ý nghĩa; lá thật bật ra đúng lúc đọc tên | lật bài, whoosh |
| 36.0–39.5 | `reading` | "Luận giải siêu chi tiết, có cả voice đọc cho bạn nghe luôn." | Bài luận giải tự cuộn; bấm Play, sóng âm chạy; sticker "Siêu chi tiết", "Có voice đọc" | pop, click |
| 39.5–43.0 | `keeper` | "Vẫn còn thắc mắc? Hỏi tiếp Keeper AI nha." | Chat: câu hỏi → "đang gõ" → câu trả lời hiện từng chữ; mèo đọc theo, gật gù | pop ×2 |
| 43.0–47.0 | `history` | "Lịch sử xem bài lưu sẵn, xem lại lúc nào cũng được." | Danh sách lịch sử trượt vào; sticker "Lưu lại hết!"; màn đêm dâng lên | pop, riser |
| 47.0–54.5 | `cta` | "Tải app Ember liền!" · "Lá bài hôm nay, nói gì với bạn?" | Logo rơi xuống & nảy, wordmark Ember; "Tải app Ember liền!!!" từng chữ; rating **4.8★** lấp đầy; mèo vẫy; rồi lắng lại: một lá bài hạ xuống, lật chậm ra The Star, câu hỏi hiện mờ-rõ từng chữ | impact, pop, lật bài, chime, nhạc lắng |

**Caption:** live caption tiếng Việt, 2–4 từ/nhóm, highlight vàng **theo từng từ** (`compositions/captions.html`, sinh từ `scripts/words.json`).
Các câu đã hiện to trên màn (hook, CTA, câu kết) không lặp caption.

**Màu:** kem `#F6EFDF`, olive nhạt `#C9D0A8` / `#8E9A6B`, navy `#24304F`, điểm nhấn vàng `#E8C27A`, hồng phấn `#F2B8B5`.
**Font:** Nunito (UI, caption), Playfair Display (tiêu đề huyền bí).
**Lá bài:** ảnh Rider-Waite 1909 (public domain, Wikimedia Commons). Mặt sau "cổ điển" và "hoa bướm" là minh họa vẽ mới (`assets/art/`).

## 3. Cấu trúc

```
index.html                 # gốc: 11 scene + captions + VO + nhạc + 54 SFX (sinh bởi scripts/build_index.py)
compositions/*.html        # mỗi scene một file
compositions/captions.html # caption karaoke (sinh bởi scripts/build_captions.py)
assets/fx.js               # PRNG có seed, mèo mascot (SVG rig), bụi sao & sparkle burst
assets/ember.css           # token màu, khung iPhone, lá bài 3D, sticker
assets/audio/              # vo.wav, music.wav, vo_lines/*.wav
assets/sfx/                # SFX (Pixabay license, từ HyperFrames) + lật bài / xáo bài / chia bài tự tổng hợp
scripts/vo_script.json     # lời thoại + mốc bắt đầu từng câu
scripts/generate_audio.sh  # multix (MiniMax + Gemini) hoặc fallback → ghép VO → caption
```

## 4. Làm lại audio bằng multix

```bash
cd ember-tarot-video
# sửa cú pháp nếu multix của bạn khác (xem multix --help):
export MULTIX_MUSIC_CMD="multix music generate --model minimax/music --duration 55"
export MULTIX_TTS_CMD="multix tts --model gemini-3.8-flash --language vi-VN"
./scripts/generate_audio.sh
npx hyperframes@0.9.36 check
npx hyperframes@0.9.36 render -o renders/ember-tarot-9x16.mp4 -q delivery
```

Giọng mới dài/ngắn khác bản tạm → chỉnh `start` trong `scripts/vo_script.json` (các mốc hình ảnh được canh theo
những mốc này). Nếu có timing từng từ chính xác (từ Gemini hoặc whisper), lưu vào `scripts/words.override.json`
(`[{line, scene, text, start, end}]`) để caption khớp tuyệt đối.

## 5. Xem & chỉnh

```bash
npx hyperframes@0.9.36 preview      # Studio preview trên trình duyệt
npx hyperframes@0.9.36 snapshot --at 1,10,27
```
