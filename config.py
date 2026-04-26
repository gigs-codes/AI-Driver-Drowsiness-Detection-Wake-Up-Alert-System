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
