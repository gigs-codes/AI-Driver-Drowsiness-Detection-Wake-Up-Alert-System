"""
utils/fatigue_score.py
----------------------
Computes a weighted fatigue risk score and applies EMA smoothing.

Risk = 0.50 × EyeClosure + 0.20 × Yawn + 0.20 × HeadPose + 0.10 × Distraction
NewRisk = alpha × current + (1 - alpha) × previous
"""

from dataclasses import dataclass, field
from typing import Optional
import config as cfg


@dataclass
class FatigueComponents:
    """Normalised component scores (each in [0.0, 1.0])."""
    eye_closure:  float = 0.0
    yawn:         float = 0.0
    head_pose:    float = 0.0
    distraction:  float = 0.0


@dataclass
class FatigueState:
    """Mutable state carried between frames."""
    # Frame counters
    eye_closed_frames:  int   = 0
    yawn_frames:        int   = 0

    # Current per-component scores
    components: FatigueComponents = field(default_factory=FatigueComponents)

    # Smoothed risk score
    smoothed_risk: float = 0.0

    # Per-session counters
    total_yawns:       int   = 0
    total_blink_events:int   = 0


# ---------------------------------------------------------------------------
# Component scorers
# ---------------------------------------------------------------------------

def eye_closure_score(ear: float, state: FatigueState) -> float:
    """
    Returns a score in [0, 1] based on consecutive closed-eye frames.
    0 → eyes open; 1 → eyes closed for MAX_CONSEC frames or longer.
    """
    if ear < cfg.EAR_THRESHOLD:
        state.eye_closed_frames += 1
    else:
        if state.eye_closed_frames >= cfg.EAR_CONSEC_FRAMES:
            state.total_blink_events += 1
        state.eye_closed_frames = 0

    # Score ramps from 0 at threshold to 1 at 3× threshold
    max_frames = cfg.EAR_CONSEC_FRAMES * 3
    return min(state.eye_closed_frames / max_frames, 1.0)


def yawn_score(mar: float, state: FatigueState) -> float:
    """
    Returns a binary-style score (0 or 1) after CONSEC frames of yawning.
    """
    if mar > cfg.MAR_THRESHOLD:
        state.yawn_frames += 1
    else:
        if state.yawn_frames >= cfg.MAR_CONSEC_FRAMES:
            state.total_yawns += 1
        state.yawn_frames = 0

    return 1.0 if state.yawn_frames >= cfg.MAR_CONSEC_FRAMES else 0.0


def head_pose_score(
    pitch: Optional[float],
    yaw:   Optional[float],
) -> float:
    """
    Returns a score in [0, 1] based on how far the head deviates from neutral.
    """
    if pitch is None or yaw is None:
        return 0.0

    pitch_excess = max(abs(pitch) - cfg.HEAD_PITCH_THRESHOLD, 0.0)
    yaw_excess   = max(abs(yaw)   - cfg.HEAD_YAW_THRESHOLD,   0.0)

    # Normalise: exceeding 2× threshold → score = 1.0
    pitch_score  = min(pitch_excess / cfg.HEAD_PITCH_THRESHOLD, 1.0)
    yaw_score    = min(yaw_excess   / cfg.HEAD_YAW_THRESHOLD,   1.0)

    return max(pitch_score, yaw_score)


def distraction_score() -> float:
    """
    Placeholder distraction detector.
    In a full implementation this would use gaze direction or phone detection.
    """
    return 0.0


# ---------------------------------------------------------------------------
# Weighted risk + EMA
# ---------------------------------------------------------------------------

def compute_risk(components: FatigueComponents) -> float:
    """Compute weighted raw risk score (0.0–1.0)."""
    return (
        cfg.W_EYE_CLOSURE * components.eye_closure
        + cfg.W_YAWN       * components.yawn
        + cfg.W_HEAD_POSE  * components.head_pose
        + cfg.W_DISTRACTION* components.distraction
    )


def apply_ema(current: float, previous: float) -> float:
    """Exponential moving average smoothing."""
    return cfg.EMA_ALPHA * current + (1.0 - cfg.EMA_ALPHA) * previous


def update_fatigue(
    ear:   float,
    mar:   float,
    pitch: Optional[float],
    yaw:   Optional[float],
    state: FatigueState,
) -> float:
    """
    Master update function called once per frame.
    Updates state in place and returns the smoothed risk score.
    """
    c = state.components
    c.eye_closure = eye_closure_score(ear, state)
    c.yawn        = yawn_score(mar, state)
    c.head_pose   = head_pose_score(pitch, yaw)
    c.distraction = distraction_score()

    raw_risk      = compute_risk(c)
    state.smoothed_risk = apply_ema(raw_risk, state.smoothed_risk)

    return state.smoothed_risk
