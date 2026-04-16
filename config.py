"""
config.py — Central configuration for DrowsGuard
All thresholds, paths, and feature flags in one place.
"""

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  Detection Thresholds
# ─────────────────────────────────────────────
EAR_THRESHOLD          = 0.22   # Eye Aspect Ratio below this → eye closed
MAR_THRESHOLD          = 0.65   # Mouth Aspect Ratio above this → yawn
HEAD_PITCH_THRESHOLD   = 15.0   # Degrees — nodding down
HEAD_YAW_THRESHOLD     = 25.0   # Degrees — looking away
BLINK_RATE_LOW         = 8      # Blinks/min below this → microsleep risk

# Time thresholds (seconds)
EYE_CLOSE_CONSECUTIVE  = 2.5    # Eyes closed this long → alert
YAWN_CONSECUTIVE       = 1.5    # Yawn held this long → counted
HEAD_DOWN_CONSECUTIVE  = 2.0    # Head down this long → alert
LOOK_AWAY_CONSECUTIVE  = 3.0    # Looking away this long → alert

# ─────────────────────────────────────────────
#  Fatigue Score Weights  (must sum to 1.0)
# ─────────────────────────────────────────────
W_EYE_CLOSURE   = 0.50
W_YAWN          = 0.20
W_HEAD_POSE     = 0.20
W_DISTRACTION   = 0.10

# ─────────────────────────────────────────────
#  Alert Levels
# ─────────────────────────────────────────────
RISK_LEVEL1 = 0.40   # Mild fatigue
RISK_LEVEL2 = 0.65   # Dangerous drowsiness
RISK_LEVEL3 = 0.85   # No response / escalate

ESCALATION_TIMEOUT = 5.0   # Seconds before escalating if no response

# ─────────────────────────────────────────────
#  MediaPipe Landmark Indices
# ─────────────────────────────────────────────
# Left eye
LEFT_EYE  = [362, 385, 387, 263, 373, 380]
# Right eye
RIGHT_EYE = [33,  160, 158, 133, 153, 144]
# Mouth (for MAR)
MOUTH_OUTER = [61, 291, 0, 17, 267, 37]
# Nose tip + chin + left/right cheek for head pose
HEAD_POSE_POINTS = [1, 152, 33, 263, 61, 291]

# ─────────────────────────────────────────────
#  Notification (optional)
# ─────────────────────────────────────────────
@dataclass
class NotificationConfig:
    enabled:           bool = False
    twilio_sid:        Optional[str] = None
    twilio_token:      Optional[str] = None
    twilio_from:       Optional[str] = None
    alert_phone:       Optional[str] = None
    telegram_token:    Optional[str] = None
    telegram_chat_id:  Optional[str] = None


# ─────────────────────────────────────────────
#  Paths
# ─────────────────────────────────────────────
ALARM_SOUND_PATH   = "assets/alarm.wav"
LOG_DIR            = "logs"
DASHBOARD_DB       = "logs/session_data.json"

# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────
DASHBOARD_REFRESH_MS = 500   # How often to refresh the live plot (ms)
HISTORY_WINDOW_SEC   = 60    # Rolling window shown in live plot

# ─────────────────────────────────────────────
#  Camera
# ─────────────────────────────────────────────
CAMERA_INDEX  = 0
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480
TARGET_FPS    = 30
