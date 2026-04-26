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
```

---

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
```

---

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
