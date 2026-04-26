"""
detector.py
-----------
Core detection pipeline.

Wraps MediaPipe Face Mesh and orchestrates:
  - Landmark extraction
  - EAR / MAR computation
  - Head pose estimation
  - Fatigue score update
  - Overlay rendering on the frame
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

import config as cfg
from alerter import Alerter, AlertLevel, NO_ALERT
from utils.ear_calculator import compute_average_ear
from utils.mar_calculator import mouth_aspect_ratio
from utils.head_pose import estimate_head_pose
from utils.fatigue_score import FatigueState, update_fatigue

log = logging.getLogger(__name__)

mp_face_mesh = mp.solutions.face_mesh
mp_drawing   = mp.solutions.drawing_utils
mp_styles    = mp.solutions.drawing_styles


# ---------------------------------------------------------------------------
# Detection result for one frame
# ---------------------------------------------------------------------------

@dataclass
class FrameResult:
    face_detected: bool  = False
    ear:           float = 0.0
    mar:           float = 0.0
    pitch: Optional[float] = None
    yaw:   Optional[float] = None
    risk:          float = 0.0
    alert: AlertLevel      = field(default_factory=lambda: NO_ALERT)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class Detector:
    """
    Stateful detector — create once, call process_frame() in a loop.
    """

    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces        = cfg.FACE_MESH_MAX_FACES,
            min_detection_confidence = cfg.FACE_MESH_MIN_DETECT_CONF,
            min_tracking_confidence  = cfg.FACE_MESH_MIN_TRACK_CONF,
            refine_landmarks     = cfg.REFINE_LANDMARKS,
        )
        self.alerter = Alerter()
        self.state   = FatigueState()
        self._frame_h = cfg.CAMERA_HEIGHT
        self._frame_w = cfg.CAMERA_WIDTH

    # ------------------------------------------------------------------
    def process_frame(self, frame: np.ndarray) -> FrameResult:
        """
        Run the full pipeline on one BGR frame.

        Parameters
        ----------
        frame : BGR numpy array from cv2.VideoCapture.read()

        Returns
        -------
        FrameResult with all measurements and the rendered overlay on frame
        (frame is modified in-place).
        """
        self._frame_h, self._frame_w = frame.shape[:2]
        result = FrameResult()

        # MediaPipe expects RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        mp_result = self.face_mesh.process(rgb)
        rgb.flags.writeable = True

        if not mp_result.multi_face_landmarks:
            self._draw_no_face_overlay(frame)
            return result

        # ── Extract pixel coordinates ──────────────────────────────────
        face_lm = mp_result.multi_face_landmarks[0]
        lm_px   = self._landmarks_to_pixels(face_lm)

        # ── Metrics ────────────────────────────────────────────────────
        ear, r_ear, l_ear = compute_average_ear(lm_px)
        mar                = mouth_aspect_ratio(lm_px)
        pitch, yaw         = estimate_head_pose(lm_px, self._frame_w, self._frame_h)
        risk               = update_fatigue(ear, mar, pitch, yaw, self.state)
        alert              = self.alerter.evaluate(risk)

        # ── Populate result ────────────────────────────────────────────
        result.face_detected = True
        result.ear           = ear
        result.mar           = mar
        result.pitch         = pitch
        result.yaw           = yaw
        result.risk          = risk
        result.alert         = alert

        # ── Draw on frame ──────────────────────────────────────────────
        self._draw_face_mesh(frame, face_lm)
        self._draw_overlay(frame, result)

        return result

    # ------------------------------------------------------------------
    def _landmarks_to_pixels(self, face_lm) -> np.ndarray:
        """Convert normalised MediaPipe landmarks → pixel coordinates."""
        pts = np.array(
            [[lm.x * self._frame_w, lm.y * self._frame_h]
             for lm in face_lm.landmark],
            dtype=np.float64,
        )
        return pts                          # shape (468+, 2)

    # ------------------------------------------------------------------
    def _draw_face_mesh(self, frame, face_lm) -> None:
        """Draw the tessellation and contours lightly."""
        mp_drawing.draw_landmarks(
            image                  = frame,
            landmark_list          = face_lm,
            connections            = mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec  = None,
            connection_drawing_spec= mp_styles.get_default_face_mesh_tesselation_style(),
        )
        mp_drawing.draw_landmarks(
            image                  = frame,
            landmark_list          = face_lm,
            connections            = mp_face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec  = None,
            connection_drawing_spec= mp_styles.get_default_face_mesh_contours_style(),
        )

    # ------------------------------------------------------------------
    def _draw_overlay(self, frame: np.ndarray, r: FrameResult) -> None:
        """Render the HUD overlay on the frame."""
        h, w = frame.shape[:2]
        fs    = cfg.OVERLAY_FONT_SCALE
        th    = cfg.OVERLAY_THICKNESS
        font  = cv2.FONT_HERSHEY_SIMPLEX
        pad   = 10

        # Risk bar background
        bar_x1, bar_y1 = pad, pad
        bar_x2, bar_y2 = pad + 200, pad + 14
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (40, 40, 40), -1)

        # Filled portion
        fill_x2 = bar_x1 + int(r.risk * 200)
        cv2.rectangle(frame, (bar_x1, bar_y1), (fill_x2, bar_y2), r.alert.color_bgr, -1)
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (100, 100, 100), 1)

        # Metric text (left column)
        lines = [
            f"Risk : {r.risk:.2f}",
            f"EAR  : {r.ear:.3f}",
            f"MAR  : {r.mar:.3f}",
            f"Pitch: {r.pitch:.1f}" if r.pitch is not None else "Pitch: --",
            f"Yaw  : {r.yaw:.1f}"   if r.yaw   is not None else "Yaw  : --",
        ]
        y_start = bar_y2 + 6
        for i, line in enumerate(lines):
            y = y_start + i * 20
            cv2.putText(frame, line, (pad, y), font, fs, (220, 220, 220), th, cv2.LINE_AA)

        # Session stats (right column)
        stats = [
            f"Yawns : {self.state.total_yawns}",
            f"Blinks: {self.state.total_blink_events}",
        ]
        for i, s in enumerate(stats):
            y = y_start + i * 20
            cv2.putText(frame, s, (w - 150, y), font, fs, (200, 200, 200), th, cv2.LINE_AA)

        # Alert banner
        if r.alert.level > 0:
            self._draw_alert_banner(frame, r.alert)

    # ------------------------------------------------------------------
    def _draw_alert_banner(self, frame: np.ndarray, alert: AlertLevel) -> None:
        """Draw a coloured alert banner at the bottom of the frame."""
        h, w = frame.shape[:2]
        bh   = 40
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - bh), (w, h), alert.color_bgr, -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        text = f"Level {alert.level} — {alert.label}: {alert.message}"
        cv2.putText(
            frame, text,
            (10, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (255, 255, 255), 2, cv2.LINE_AA,
        )

    # ------------------------------------------------------------------
    def _draw_no_face_overlay(self, frame: np.ndarray) -> None:
        """Show a notice when no face is detected."""
        cv2.putText(
            frame,
            "No face detected — please face the camera",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (0, 200, 255), 2, cv2.LINE_AA,
        )

    # ------------------------------------------------------------------
    def release(self) -> None:
        """Clean up MediaPipe resources."""
        self.face_mesh.close()
