"""
utils/ear_calculator.py
-----------------------
Computes the Eye Aspect Ratio (EAR) from MediaPipe Face Mesh landmarks.

EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)

Reference landmark indices (MediaPipe 468-point face mesh):
  Right eye: [33, 160, 158, 133, 153, 144]
  Left eye : [362, 385, 387, 263, 373, 380]
"""

import numpy as np
from typing import List, Tuple


# ---------------------------------------------------------------------------
# MediaPipe landmark indices for each eye
# Order: [outer_corner, upper1, upper2, inner_corner, lower1, lower2]
# ---------------------------------------------------------------------------
RIGHT_EYE_INDICES: List[int] = [33, 160, 158, 133, 153, 144]
LEFT_EYE_INDICES:  List[int] = [362, 385, 387, 263, 373, 380]


def _euclidean(p1: np.ndarray, p2: np.ndarray) -> float:
    """Return the Euclidean distance between two 2-D points."""
    return float(np.linalg.norm(p1 - p2))


def eye_aspect_ratio(landmarks: np.ndarray, eye_indices: List[int]) -> float:
    """
    Compute EAR for one eye.

    Parameters
    ----------
    landmarks   : (N, 2) array of (x, y) pixel coordinates for all landmarks.
    eye_indices : 6 landmark indices in the order described above.

    Returns
    -------
    ear : float  (0.0 when fully closed, ~0.25–0.35 when open)
    """
    p = landmarks[eye_indices]          # shape (6, 2)

    # Vertical distances
    v1 = _euclidean(p[1], p[5])        # upper1 ↔ lower1
    v2 = _euclidean(p[2], p[4])        # upper2 ↔ lower2

    # Horizontal distance
    h  = _euclidean(p[0], p[3])        # outer_corner ↔ inner_corner

    if h < 1e-6:
        return 0.0

    return (v1 + v2) / (2.0 * h)


def compute_average_ear(landmarks: np.ndarray) -> Tuple[float, float, float]:
    """
    Compute EAR for both eyes and return the average.

    Returns
    -------
    (avg_ear, right_ear, left_ear)
    """
    right = eye_aspect_ratio(landmarks, RIGHT_EYE_INDICES)
    left  = eye_aspect_ratio(landmarks, LEFT_EYE_INDICES)
    avg   = (right + left) / 2.0
    return avg, right, left
