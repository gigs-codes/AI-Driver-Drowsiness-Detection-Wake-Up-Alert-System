# 🚗 DrowsGuard — AI Driver Drowsiness Detection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-ComputerVision-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh-00BFA5)
![Real-Time](https://img.shields.io/badge/Real--Time-Detection-red)
![CPU Only](https://img.shields.io/badge/CPU-Optimized-success)
![License](https://img.shields.io/badge/License-MIT-green)

### Real-Time AI Driver Fatigue Monitoring Using Computer Vision, Facial Landmark Tracking & Intelligent Risk Scoring

*Production-ready driver drowsiness detection system powered by MediaPipe Face Mesh, OpenCV, and real-time fatigue analytics.*

</div>

---

# 📌 Overview

**DrowsGuard** is a real-time AI-powered driver drowsiness detection system designed to improve road safety through intelligent fatigue monitoring and behavioral analysis.

The platform leverages:

- Computer Vision
- Facial Landmark Detection
- Head Pose Estimation
- Eye Aspect Ratio (EAR)
- Mouth Aspect Ratio (MAR)
- Real-time fatigue scoring
- Smart alert escalation systems

to detect signs of:

- Eye closure
- Yawning
- Head nodding
- Driver distraction
- Fatigue accumulation

Built entirely using CPU-optimized pipelines, the system runs efficiently on standard laptops and embedded systems without requiring GPU acceleration.

---

# 🚀 Core Features

## 👁️ Real-Time Eye Tracking

- Eye Aspect Ratio (EAR) computation
- Blink detection & duration tracking
- Eye closure monitoring
- Microsleep detection logic
- Fatigue-aware blink analytics

---

## 😮 AI Yawn Detection

- Mouth Aspect Ratio (MAR) analysis
- Consecutive yawn duration monitoring
- Fatigue-induced yawning detection
- Real-time facial landmark tracking

---

## 🤕 Head Pose Estimation

- 6-point 3D facial landmark model
- solvePnP-based head orientation
- Pitch / yaw / roll estimation
- Driver distraction monitoring
- Look-away detection

---

## 🧠 Intelligent Fatigue Scoring

- Weighted fatigue risk formula
- Exponential Moving Average (EMA) smoothing
- Multi-factor behavioral fusion
- Real-time risk accumulation
- Alert escalation logic

---

## 🔊 Smart Alert System

- 3-level alert escalation
- Offline voice alerts using pyttsx3
- Audible alarms
- Recovery-aware cancellation
- Escalation timeout monitoring

---

## 📊 Live Dashboard & Analytics

- Real-time fatigue graph
- Rolling-window analytics
- Eye/yawn/head metrics visualization
- Session logging
- Performance monitoring dashboard

---

# 🏗️ System Architecture

```text
 Webcam Input
       │
       ▼
┌─────────────────────┐
│ MediaPipe Face Mesh │
│ Facial Landmarks    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Feature Extraction  │
│ EAR • MAR • Pose    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Fatigue Risk Engine │
│ EMA + Weighted Risk │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Alert System        │
│ Voice + Dashboard   │
└─────────────────────┘
```

---

# 🧩 Tech Stack

## Core Technologies

- **Python**
- **OpenCV**
- **MediaPipe Face Mesh**
- **NumPy**
- **Matplotlib**

---

## AI / Vision Components

- **Facial Landmark Detection**
- **solvePnP Head Pose Estimation**
- **EAR & MAR Metrics**
- **Fatigue Risk Modeling**

---

## Audio & Alerts

- **pyttsx3**
- **Offline Voice Alerts**
- **Alarm Escalation Logic**

---

# 📂 Project Structure

```bash
drowsguard/
│
├── main.py              # Entry point & webcam loop
├── detector.py          # MediaPipe pipeline + overlays
├── alerter.py           # Multi-level alert system
├── dashboard.py         # Real-time matplotlib dashboard
├── config.py            # Tunable thresholds & constants
├── requirements.txt
│
├── utils/
│   ├── ear_calculator.py    # Eye Aspect Ratio logic
│   ├── mar_calculator.py    # Mouth Aspect Ratio logic
│   ├── head_pose.py         # solvePnP head pose estimation
│   └── fatigue_score.py     # Weighted risk scoring + EMA
│
├── tests/
│   └── test_detection.py    # Pytest unit tests
│
└── assets/
    └── alarm.wav
```

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/drowsguard.git

cd drowsguard
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv .venv

source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run Application

```bash
python main.py
```

---

# 🎮 Runtime Controls

| Key | Action |
|------|------|
| `q` | Quit application |
| `d` | Toggle dashboard |
| `m` | Toggle face mesh overlay |
| `r` | Reset fatigue state |

---

# ⚙️ CLI Options

```bash
# Use external webcam
python main.py --camera 1

# Disable dashboard
python main.py --no-dashboard

# Custom resolution
python main.py --width 1280 --height 720

# Video file input
python main.py --source video.mp4

# Enable notifications
python main.py --notify
```

---

# 🧠 Fatigue Scoring Formula

```text
Risk =
0.50 × EyeClosure +
0.20 × Yawn +
0.20 × HeadPose +
0.10 × Distraction
```

---

# 📈 EMA Smoothing

```text
SmoothedRisk =
0.30 × CurrentRisk +
0.70 × PreviousRisk
```

---

# 🚨 Alert Escalation Levels

| Level | Threshold | Action |
|------|------|------|
| Level 1 — Caution | ≥ 0.40 | Soft beep + voice warning |
| Level 2 — Warning | ≥ 0.65 | Siren + alert escalation |
| Level 3 — Critical | ≥ 0.85 | Continuous alarm + notifications |

---

# 📊 Live Dashboard

The live matplotlib dashboard visualizes:

- Fatigue risk score
- Eye closure metrics
- Yawn activity
- Head movement analytics
- Alert thresholds
- Rolling session trends

Session data is logged for analytics and debugging.

---

# 📲 Remote Notifications (Optional)

Supports:

- Twilio SMS alerts
- Telegram bot notifications

## Example Environment Variables

```bash
# Twilio
export TWILIO_SID="ACxxxx"
export TWILIO_TOKEN="xxxx"
export TWILIO_FROM="+123456789"
export ALERT_PHONE="+987654321"

# Telegram
export TELEGRAM_TOKEN="bot_token"
export TELEGRAM_CHAT_ID="chat_id"
```

---

# ⚙️ Configuration Reference

All configurable thresholds are centralized in `config.py`.

| Constant | Default | Description |
|------|------|------|
| `EAR_THRESHOLD` | 0.22 | Eye closure threshold |
| `MAR_THRESHOLD` | 0.65 | Yawn threshold |
| `HEAD_PITCH_THRESHOLD` | 15° | Forward nod angle |
| `HEAD_YAW_THRESHOLD` | 25° | Look-away threshold |
| `EMA_ALPHA` | 0.30 | EMA smoothing factor |
| `RISK_LEVEL1/2/3` | 0.40 / 0.65 / 0.85 | Alert thresholds |

---

# 🧪 Testing

## Run Tests

```bash
pytest tests/ -v --cov=.
```

---

## Test Coverage Includes

- EAR open/closed discrimination
- MAR yawn detection
- Fatigue score weighting
- EMA smoothing validation
- Alert escalation logic
- Blink tracker accuracy
- Duration timer behavior

---

# 📈 Performance Benchmarks

| Hardware | Resolution | FPS |
|------|------|------|
| MacBook Pro M2 | 640×480 | ~30 FPS |
| Intel i7 Laptop | 640×480 | ~24 FPS |
| Raspberry Pi 4 | 320×240 | ~12 FPS |

### Optimization Notes

- CPU-only inference
- MediaPipe optimized C++ backend
- Dashboard capped at 10 Hz refresh
- Lightweight facial landmark pipeline

---

# 🔥 Engineering Highlights

✅ Built real-time AI fatigue monitoring system using MediaPipe Face Mesh  
✅ Implemented CPU-optimized facial landmark inference pipelines  
✅ Developed intelligent fatigue scoring engine using EAR, MAR & head pose  
✅ Designed multi-level alert escalation architecture with recovery logic  
✅ Integrated real-time analytics dashboard for fatigue visualization  
✅ Built modular and extensible computer vision architecture  
✅ Enabled offline voice alert system without cloud dependencies  
✅ Developed configurable safety-critical threshold management system  

---

# 🛣️ Future Roadmap

- PERCLOS fatigue metric implementation
- YOLO-based phone usage detection
- Smoking detection module
- Temporal deep learning microsleep classification
- Flutter mobile companion application
- Streamlit fleet management dashboard
- ONNX export for edge deployment
- Real-time cloud telemetry support

---

# 🌍 Potential Applications

- Smart vehicle safety systems
- Fleet management monitoring
- Commercial transportation safety
- Driver behavior analytics
- Automotive AI research
- Embedded edge AI systems

---

# 🔐 Scalability & Reliability

- CPU-efficient inference
- Modular architecture
- Configurable thresholds
- Offline-first alerting
- Embedded device compatibility
- Extensible detection pipelines

---

# 🤝 Contributing

Contributions, optimizations, and safety improvements are welcome.

```bash
# Fork repository
# Create feature branch
git checkout -b feature/amazing-feature

# Commit changes
git commit -m "Add amazing feature"

# Push branch
git push origin feature/amazing-feature
```

Please run:

```bash
pytest
flake8
```

before submitting PRs.

---

# 📜 License

MIT License © 2026

See `LICENSE` for details.

---

# 📚 References

- Soukupová & Čech (2016) — Real-Time Eye Blink Detection
- MediaPipe Face Mesh Documentation
- NHTSA Drowsy Driving Research
- OpenCV solvePnP Head Pose Estimation

---

# 👨‍💻 Resume-Friendly Description

> Built a real-time AI-powered driver drowsiness detection system using MediaPipe Face Mesh, OpenCV, EAR/MAR-based fatigue analysis, solvePnP head pose estimation, and intelligent multi-level alert escalation with live analytics dashboards and offline voice alerts.

---

# 🌟 Why This Project Stands Out

This project demonstrates expertise in:

- Computer Vision Engineering
- Real-Time AI Systems
- Facial Landmark Analysis
- Edge AI Optimization
- OpenCV Development
- MediaPipe Pipelines
- Human Behavior Analytics
- Embedded AI Systems
- Safety-Critical AI Applications
- Real-Time Monitoring Systems

---

<div align="center">

### ⭐ If you found this project valuable, consider starring the repository.

</div>
