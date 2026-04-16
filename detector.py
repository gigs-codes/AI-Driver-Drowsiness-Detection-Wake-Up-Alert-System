"""
detector.py — Core detection pipeline for DrowsGuard
Wraps MediaPipe Face Mesh and orchestrates EAR / MAR / HeadPose / Fatigue.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple

import cv2
import numpy as np
import mediapipe as mp

import config as cfg
from utils.ear_calculator import both_eyes_ear, is_eye_closed
from utils.mar_calculator import mouth_aspect_ratio, is_yawning
from utils.head_pose       import estimate_head_pose, is_head_nodding, is_looking_away
from utils.fatigue_score   import FatigueScoreCalculator

logger = logging.getLogger(__name__)

mp_face_mesh = mp.solutions.face_mesh
mp_drawing   = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


# ─────────────────────────────────────────────
#  Detection result dataclass
# ─────────────────────────────────────────────
@dataclass
class FrameResult:
    face_detected:    bool    = False
    ear:              float   = 0.0
    mar:              float   = 0.0
    pitch:            float   = 0.0
    yaw:              float   = 0.0
    roll:             float   = 0.0
    eye_closed:       bool    = False
    yawning:          bool    = False
    head_nodding:     bool    = False
    looking_away:     bool    = False
    fatigue_score:    float   = 0.0
    alert_level:      int     = 0
    blinks_per_min:   float   = 0.0
    eye_score:        float   = 0.0
    yawn_score:       float   = 0.0
    head_score:       float   = 0.0
    distraction_score:float   = 0.0
    annotated_frame:  Optional[np.ndarray] = field(default=None, repr=False)


# ─────────────────────────────────────────────
#  Overlay drawing helpers
# ─────────────────────────────────────────────
LEVEL_COLORS = {
    0: (0,   200,  50),    # green
    1: (0,   200, 255),    # yellow-ish
    2: (0,   120, 255),    # orange
    3: (0,    0,  255),    # red
}

LEVEL_LABELS = {
    0: "ALERT",
    1: "MILD FATIGUE",
    2: "DANGEROUS",
    3: "CRITICAL",
}


def _draw_bar(frame, label, value, y, color, width=200):
    h = 12
    x = 10
    cv2.rectangle(frame, (x, y), (x + width, y + h), (50, 50, 50), -1)
    cv2.rectangle(frame, (x, y), (x + int(width * value), y + h), color, -1)
    cv2.putText(frame, f"{label}: {value:.2f}", (x + width + 6, y + 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)


def _draw_hud(frame: np.ndarray, result: FrameResult) -> np.ndarray:
    """Render heads-up display onto frame."""
    h, w = frame.shape[:2]
    level  = result.alert_level
    color  = LEVEL_COLORS[level]
    label  = LEVEL_LABELS[level]

    # ── Status banner (top)
    banner_h = 36
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, banner_h), (20, 20, 20), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

    cv2.putText(frame, f"DrowsGuard  |  {label}", (10, 24),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"Risk: {result.fatigue_score:.2f}", (w - 140, 24),
                cv2.FONT_HERSHEY_DUPLEX, 0.65, color, 1, cv2.LINE_AA)

    # ── Red flash overlay on Level 3
    if level == 3:
        red_overlay = frame.copy()
        cv2.rectangle(red_overlay, (0, 0), (w, h), (0, 0, 180), -1)
        frame = cv2.addWeighted(red_overlay, 0.25, frame, 0.75, 0)

    if not result.face_detected:
        cv2.putText(frame, "No face detected", (10, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        return frame

    # ── Component bars (bottom-left)
    base_y = h - 80
    _draw_bar(frame, "Eyes",        result.eye_score,          base_y,      (100, 220, 100))
    _draw_bar(frame, "Yawn",        result.yawn_score,          base_y + 18, (100, 180, 255))
    _draw_bar(frame, "Head",        result.head_score,          base_y + 36, (255, 180,  60))
    _draw_bar(frame, "Distract",    result.distraction_score,   base_y + 54, (180, 100, 255))

    # ── Metric text (top-right)
    metrics = [
        f"EAR:   {result.ear:.3f}",
        f"MAR:   {result.mar:.3f}",
        f"Pitch: {result.pitch:+.1f}°",
        f"Yaw:   {result.yaw:+.1f}°",
        f"BPM:   {result.blinks_per_min:.1f}",
    ]
    for i, line in enumerate(metrics):
        cv2.putText(frame, line, (w - 150, 55 + i * 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1, cv2.LINE_AA)

    # ── Alert box
    if level > 0:
        msg = ["", "Stay alert!", "Wake up now!", "WAKE UP — PULL OVER"][level]
        (tw, th), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)
        tx = (w - tw) // 2
        ty = h // 2
        cv2.rectangle(frame, (tx - 10, ty - th - 10), (tx + tw + 10, ty + 8),
                      color, -1)
        cv2.putText(frame, msg, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                    (10, 10, 10), 2, cv2.LINE_AA)

    return frame


# ─────────────────────────────────────────────
#  Detector class
# ─────────────────────────────────────────────
class DrowsinessDetector:
    """
    Main detection pipeline.

    Usage
    -----
    detector = DrowsinessDetector()
    result   = detector.process(frame)
    """

    def __init__(self, draw_mesh: bool = False):
        self.draw_mesh = draw_mesh
        self._face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._fatigue = FatigueScoreCalculator()
        self._frame_count = 0

    # ── Main entry-point ────────────────────
    def process(self, frame: np.ndarray) -> FrameResult:
        """Process one BGR camera frame.  Returns a FrameResult."""
        self._frame_count += 1
        result = FrameResult()
        h, w = frame.shape[:2]

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_result = self._face_mesh.process(rgb)

        annotated = frame.copy()

        if not mp_result.multi_face_landmarks:
            result.annotated_frame = _draw_hud(annotated, result)
            return result

        result.face_detected = True
        face_lm = mp_result.multi_face_landmarks[0]

        # Convert landmarks to pixel coords
        lm_arr = np.array(
            [(lm.x * w, lm.y * h) for lm in face_lm.landmark],
            dtype=np.float32,
        )

        # ── EAR
        result.ear = both_eyes_ear(lm_arr, cfg.LEFT_EYE, cfg.RIGHT_EYE)
        result.eye_closed = is_eye_closed(result.ear, cfg.EAR_THRESHOLD)

        # ── MAR
        result.mar = mouth_aspect_ratio(lm_arr, cfg.MOUTH_OUTER)
        result.yawning = is_yawning(result.mar, cfg.MAR_THRESHOLD)

        # ── Head pose
        pose = estimate_head_pose(lm_arr, w, h)
        if pose:
            result.pitch, result.yaw, result.roll = pose
            result.head_nodding = is_head_nodding(result.pitch, cfg.HEAD_PITCH_THRESHOLD)
            result.looking_away = is_looking_away(result.yaw,   cfg.HEAD_YAW_THRESHOLD)

        # ── Fatigue score
        score = self._fatigue.update(
            ear=result.ear,
            eye_closed=result.eye_closed,
            mar=result.mar,
            yawning=result.yawning,
            head_nodding=result.head_nodding,
            looking_away=result.looking_away,
        )
        result.fatigue_score     = score
        result.alert_level       = self._fatigue.alert_level()
        result.blinks_per_min    = self._fatigue.blink_tracker.blinks_per_minute
        result.eye_score         = self._fatigue.eye_score
        result.yawn_score        = self._fatigue.yawn_score
        result.head_score        = self._fatigue.head_pose_score
        result.distraction_score = self._fatigue.distraction_score

        # ── Draw mesh (optional)
        if self.draw_mesh:
            mp_drawing.draw_landmarks(
                image=annotated,
                landmark_list=face_lm,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style(),
            )

        result.annotated_frame = _draw_hud(annotated, result)
        return result

    def release(self):
        self._face_mesh.close()

    # ── Attentiveness check ─────────────────
    @staticmethod
    def is_attentive(result: FrameResult) -> bool:
        """True when driver appears to have responded to the alert."""
        return (
            not result.eye_closed
            and not result.head_nodding
            and result.ear > cfg.EAR_THRESHOLD * 1.1
        )
