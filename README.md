<<<<<<< HEAD
# DrowsGuard — AI Driver Drowsiness Detection System

Real-time CPU-only drowsiness detection using MediaPipe Face Mesh, OpenCV, and Python.

---

## Features

| Feature | Implementation |
|---|---|
| Eye tracking | Eye Aspect Ratio (EAR) via MediaPipe |
| Yawn detection | Mouth Aspect Ratio (MAR) |
| Head pose estimation | solvePnP with 6-point 3-D face model |
| Distraction detection | Placeholder (extensible) |
| Fatigue scoring | Weighted formula + EMA smoothing |
| Voice alerts | pyttsx3 (offline, no API key) |
| Live dashboard | Matplotlib rolling-window graph |

---

## Quickstart

```bash
# 1. Clone / download the project
cd drowsguard

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `q` | Quit |
| `d` | Toggle matplotlib dashboard |
| `r` | Reset fatigue state & counters |

### CLI flags

```bash
python main.py --camera 1          # Use external webcam
python main.py --no-dashboard      # Disable matplotlib window
python main.py --width 1280 --height 720
```

---

## Project Structure

```
drowsguard/
├── main.py              # Entry point & webcam loop
├── detector.py          # MediaPipe pipeline + overlay rendering
├── alerter.py           # 3-level alert system with voice (pyttsx3)
├── dashboard.py         # Real-time matplotlib dashboard
├── config.py            # All tunable constants
├── requirements.txt
├── utils/
│   ├── ear_calculator.py   # Eye Aspect Ratio
│   ├── mar_calculator.py   # Mouth Aspect Ratio
│   ├── head_pose.py        # solvePnP head pose estimation
│   └── fatigue_score.py    # Weighted scoring + EMA smoothing
├── tests/
│   └── test_detection.py   # pytest test suite
└── assets/
    └── alarm_placeholder.txt
=======
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
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
```

---

<<<<<<< HEAD
## Fatigue Scoring Formula

```
Risk = 0.50 × EyeClosure
     + 0.20 × Yawn
     + 0.20 × HeadPose
     + 0.10 × Distraction

SmoothedRisk = 0.30 × Risk + 0.70 × PreviousRisk
```

## Alert Levels

| Level | Threshold | Voice message |
|-------|-----------|---------------|
| 1 — Caution  | ≥ 0.40 | "Please focus"  |
| 2 — Warning  | ≥ 0.65 | "Stay alert!"  |
| 3 — Critical | ≥ 0.85 | "Wake up!"     |

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
=======
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
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
```

---

<<<<<<< HEAD
## Performance

Tested on a 2021 laptop with integrated Intel graphics:
- **~25–30 FPS** at 640×480 (CPU only)
- MediaPipe's optimised C++ backend handles landmark inference
- Dashboard redraws at most 10 Hz to protect frame rate

---

## Configuration

All thresholds live in `config.py`. Key parameters:

```python
EAR_THRESHOLD      = 0.22   # Eye closed below this
MAR_THRESHOLD      = 0.55   # Yawn above this
HEAD_PITCH_THRESHOLD = 15.0 # Degrees forward nod
HEAD_YAW_THRESHOLD   = 20.0 # Degrees sideways turn
EMA_ALPHA          = 0.30   # Smoothing factor
```

---

## License

MIT — free to use and extend.
=======
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
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
