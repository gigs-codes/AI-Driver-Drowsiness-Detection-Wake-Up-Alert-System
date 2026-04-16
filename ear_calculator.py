"""
utils/ear_calculator.py
Computes the Eye Aspect Ratio (EAR) from MediaPipe face-mesh landmarks.

EAR = (‖p2−p6‖ + ‖p3−p5‖) / (2 · ‖p1−p4‖)

References:
    Soukupová & Čech (2016) – Real-Time Eye Blink Detection using Facial Landmarks
"""

import numpy as np
from typing import List


def _dist(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two 2-D points."""
    return float(np.linalg.norm(a - b))


def eye_aspect_ratio(landmarks: np.ndarray, eye_indices: List[int]) -> float:
    """
    Compute EAR for one eye.

    Parameters
    ----------
    landmarks    : (N, 2) array of (x, y) pixel coordinates for all landmarks.
    eye_indices  : 6-element list → [p1, p2, p3, p4, p5, p6]
                   ordered as: outer-corner, upper-1, upper-2,
                               inner-corner, lower-2, lower-1

    Returns
    -------
    ear : float  — 0.0 (fully closed) … ~0.35 (fully open)
    """
    if len(eye_indices) != 6:
        raise ValueError("eye_indices must contain exactly 6 landmark indices.")

    pts = landmarks[eye_indices]          # shape (6, 2)
    p1, p2, p3, p4, p5, p6 = pts

    vertical_1 = _dist(p2, p6)
    vertical_2 = _dist(p3, p5)
    horizontal = _dist(p1, p4)

    if horizontal < 1e-6:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def both_eyes_ear(landmarks: np.ndarray,
                  left_indices: List[int],
                  right_indices: List[int]) -> float:
    """Average EAR across both eyes (more robust than single-eye)."""
    left  = eye_aspect_ratio(landmarks, left_indices)
    right = eye_aspect_ratio(landmarks, right_indices)
    return (left + right) / 2.0


def is_eye_closed(ear: float, threshold: float) -> bool:
    return ear < threshold
