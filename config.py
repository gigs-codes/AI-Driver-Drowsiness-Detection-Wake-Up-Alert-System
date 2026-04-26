<<<<<<< HEAD
# =============================================================================
# DrowsGuard - Configuration
# All tunable constants live here. Adjust thresholds to suit your environment.
# =============================================================================

# ---------------------------------------------------------------------------
# MediaPipe model settings
# ---------------------------------------------------------------------------
FACE_MESH_MAX_FACES       = 1        # Only track the driver's face
FACE_MESH_MIN_DETECT_CONF = 0.5      # Detection confidence threshold
FACE_MESH_MIN_TRACK_CONF  = 0.5      # Tracking confidence threshold
REFINE_LANDMARKS          = True     # Enables iris landmarks (needed for EAR)

# ---------------------------------------------------------------------------
# Eye Aspect Ratio (EAR)
# ---------------------------------------------------------------------------
EAR_THRESHOLD             = 0.22     # Below this → eye is considered closed
EAR_CONSEC_FRAMES         = 3        # Consecutive frames before counting closure

# ---------------------------------------------------------------------------
# Mouth Aspect Ratio (MAR)
# ---------------------------------------------------------------------------
MAR_THRESHOLD             = 0.55     # Above this → yawn detected
MAR_CONSEC_FRAMES         = 15       # Consecutive frames to confirm a yawn

# ---------------------------------------------------------------------------
# Head pose (degrees)
# ---------------------------------------------------------------------------
HEAD_PITCH_THRESHOLD      = 15.0     # Nodding forward (chin down)
HEAD_YAW_THRESHOLD        = 20.0     # Looking sideways

# ---------------------------------------------------------------------------
# Fatigue scoring weights  (must sum to 1.0)
# ---------------------------------------------------------------------------
W_EYE_CLOSURE             = 0.50
W_YAWN                    = 0.20
W_HEAD_POSE               = 0.20
W_DISTRACTION             = 0.10

# ---------------------------------------------------------------------------
# EMA (Exponential Moving Average) smoothing
# ---------------------------------------------------------------------------
EMA_ALPHA                 = 0.30     # Higher = more responsive, more jittery

# ---------------------------------------------------------------------------
# Alert thresholds (smoothed risk score, 0.0–1.0)
# ---------------------------------------------------------------------------
ALERT_LEVEL_1             = 0.40     # Soft warning
ALERT_LEVEL_2             = 0.65     # Strong warning
ALERT_LEVEL_3             = 0.85     # Critical alert

# Alert cooldown — minimum seconds between voice alerts of the same level
ALERT_COOLDOWN_SECONDS    = 5.0

# ---------------------------------------------------------------------------
# Dashboard / display
# ---------------------------------------------------------------------------
DASHBOARD_HISTORY_SECONDS = 60       # How many seconds of history to plot
DASHBOARD_UPDATE_INTERVAL = 0.1      # Redraw dashboard every N seconds
OVERLAY_FONT_SCALE        = 0.55
OVERLAY_THICKNESS         = 1

# ---------------------------------------------------------------------------
# Webcam
# ---------------------------------------------------------------------------
CAMERA_INDEX              = 0        # 0 = default webcam
CAMERA_WIDTH              = 640
CAMERA_HEIGHT             = 480
TARGET_FPS                = 30
=======
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
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
