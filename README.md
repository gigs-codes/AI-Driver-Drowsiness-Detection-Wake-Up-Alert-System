# 🚗 DrowsGuard — AI Driver Drowsiness Detection

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9%2B-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-00897B)
![License](https://img.shields.io/badge/License-MIT-green)
![CI](https://img.shields.io/github/actions/workflow/status/YOUR_USERNAME/drowsguard/ci.yml?label=CI&logo=github)

**Real-time driver drowsiness detection using computer vision and facial landmark analysis.**  
Detects eye closure, yawning, head nodding, and distraction — then escalates smart alerts
before it's too late.

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 👁️ **Eye tracking** | Eye Aspect Ratio (EAR) with sub-frame blink detection |
| 😮 **Yawn detection** | Mouth Aspect Ratio (MAR) with duration gating |
| 🤕 **Head pose** | 6-DoF solvePnP estimation — nod + look-away |
| 🧠 **Fatigue score** | Weighted formula with EMA smoothing |
| 🔊 **Smart alerts** | 3-level escalation — soft beep → siren → critical flash |
| 🗣️ **Voice prompts** | Offline TTS via pyttsx3 |
| 📊 **Live dashboard** | Real-time matplotlib risk + component chart |
| 📝 **Session logging** | Per-frame CSV + JSON session summaries |
| 📲 **Remote alerts** | Optional Twilio SMS / Telegram bot |
| ⚡ **No GPU needed** | Runs on CPU at 30 FPS on a laptop webcam |

---

## 🧠 Detection Algorithm

### Fatigue Score Formula

```
Risk = 0.50 × EyeClosure + 0.20 × Yawn + 0.20 × HeadPose + 0.10 × Distraction
```

Each component is independently thresholded by duration (in seconds) so a single-frame flicker never fires an alert.

### Alert Escalation

```
Risk ≥ 0.40  →  Level 1 · Mild Fatigue       → soft beep  + "Please focus on the road."
Risk ≥ 0.65  →  Level 2 · Dangerous           → siren      + "Wake up! Please stay alert."
Risk ≥ 0.85  →  Level 3 · No Response         → continuous + red flash + SMS / Telegram
```

After every alert the system checks for driver recovery (eyes open, head up).  
If the driver responds → alert cancelled.  
If the driver does **not** respond within 5 s → level escalates automatically.

---

## 🏗️ Architecture

```
drowsguard/
├── main.py                   # CLI entry point + camera loop
├── detector.py               # MediaPipe pipeline → FrameResult
├── alerter.py                # 3-level smart alert state machine
├── dashboard.py              # Session logger + live matplotlib chart
├── config.py                 # All thresholds in one place
├── utils/
│   ├── ear_calculator.py     # Eye Aspect Ratio (EAR)
│   ├── mar_calculator.py     # Mouth Aspect Ratio (MAR)
│   ├── head_pose.py          # solvePnP head pose (pitch/yaw/roll)
│   └── fatigue_score.py      # Weighted scoring + blink tracker
├── tests/
│   └── test_detection.py     # pytest unit tests
├── assets/
│   └── alarm.wav             # Alarm sound file (add your own)
└── .github/workflows/ci.yml  # GitHub Actions CI
```

---

## 🚀 Quick Start

### 1 · Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/drowsguard.git
cd drowsguard

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2 · Add an alarm sound

Place any `.wav` file at `assets/alarm.wav`.  
Free options: [Freesound.org](https://freesound.org) or `assets/generate_tone.py` (see below).

### 3 · Run

```bash
# Live webcam
python main.py

# From a video file
python main.py --source path/to/video.mp4

# Show face mesh overlay
python main.py --mesh

# Headless / no dashboard (embedded / Raspberry Pi)
python main.py --no-dashboard

# Custom thresholds
python main.py --ear-thresh 0.20 --risk1 0.35 --risk2 0.60 --risk3 0.80
```

### Key bindings (while running)
| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Reset session counters |
| `m` | Toggle face mesh overlay |

---

## 📊 Live Dashboard

A matplotlib window shows a **60-second rolling window** of:

- **Fatigue Risk** (blue line) with threshold guidelines
- **Eye / Yawn / Head / Distraction** component scores

Session data is written to `logs/session_YYYYMMDD_HHMMSS.csv` and a cumulative
summary is appended to `logs/session_data.json` after each run.

---

## 📲 Remote Notifications (Optional)

Set environment variables, then run with `--notify`:

```bash
# Twilio SMS
export TWILIO_SID="ACxxxx"
export TWILIO_TOKEN="xxxx"
export TWILIO_FROM="+1234567890"
export ALERT_PHONE="+0987654321"

# Telegram bot
export TELEGRAM_TOKEN="bot_token_here"
export TELEGRAM_CHAT_ID="chat_id_here"

python main.py --notify
```

---

## ⚙️ Configuration Reference

All tuneable constants live in `config.py`:

| Constant | Default | Description |
|---|---|---|
| `EAR_THRESHOLD` | `0.22` | EAR below this = eyes closed |
| `MAR_THRESHOLD` | `0.65` | MAR above this = yawning |
| `EYE_CLOSE_CONSECUTIVE` | `2.5 s` | Duration before eye-close counts |
| `YAWN_CONSECUTIVE` | `1.5 s` | Duration before yawn counts |
| `HEAD_PITCH_THRESHOLD` | `15°` | Chin-drop angle |
| `HEAD_YAW_THRESHOLD` | `25°` | Look-away angle |
| `RISK_LEVEL1/2/3` | `0.40 / 0.65 / 0.85` | Alert thresholds |
| `ESCALATION_TIMEOUT` | `5.0 s` | No-response window before escalation |

---

## 🧪 Tests

```bash
pytest tests/ -v --cov=.
```

Test coverage includes:
- EAR open/closed discrimination
- MAR yawn detection
- Fatigue score weights and EMA
- Alert level thresholds
- Blink tracker accuracy
- DurationTimer reset behaviour

---

## 📈 Performance

| Hardware | Resolution | FPS |
|---|---|---|
| MacBook Pro M2 | 640×480 | ~30 |
| Intel i7 laptop (CPU-only) | 640×480 | ~24 |
| Raspberry Pi 4 (4 GB) | 320×240 | ~12 |

MediaPipe Face Mesh runs entirely on CPU — **no GPU required**.

---

## 🗺️ Roadmap

- [ ] PERCLOS implementation (% eye closure over 80-second window)
- [ ] YOLO-based phone usage / smoking detection
- [ ] PyTorch temporal model for microsleep classification
- [ ] Flutter mobile companion app (phone vibration alert)
- [ ] Streamlit web dashboard for fleet managers
- [ ] ONNX export for edge inference

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit: `git commit -m "feat: add my feature"`
4. Push: `git push origin feat/my-feature`
5. Open a Pull Request

Please run `pytest` and `flake8` before submitting.

---

## 📄 License

MIT © 2024 — see [LICENSE](LICENSE) for details.

---

## 📚 References

- Soukupová & Čech (2016) — *Real-Time Eye Blink Detection using Facial Landmarks*
- MediaPipe Face Mesh — [developers.google.com/mediapipe](https://developers.google.com/mediapipe)
- NHTSA — *Drowsy Driving Research and Program Plan* (2022)
