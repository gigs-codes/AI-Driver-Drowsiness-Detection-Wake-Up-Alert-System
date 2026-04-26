"""
utils/mar_calculator.py
-----------------------
Computes the Mouth Aspect Ratio (MAR) from MediaPipe Face Mesh landmarks.

MAR = (||p2-p8|| + ||p3-p7|| + ||p4-p6||) / (2 × ||p1-p5||)

MediaPipe outer-lip landmark indices used:
  p1  (left corner)   : 61
  p2  (upper-left)    : 39
  p3  (upper-center)  : 0   (top of upper lip)
  p4  (upper-right)   : 269
  p5  (right corner)  : 291
  p6  (lower-right)   : 405
  p7  (lower-center)  : 17  (bottom of lower lip)
  p8  (lower-left)    : 181
"""

import numpy as np
from typing import List


# Outer-lip landmark indices (8-point approximation)
MOUTH_INDICES: List[int] = [61, 39, 0, 269, 291, 405, 17, 181]


def _euclidean(p1: np.ndarray, p2: np.ndarray) -> float:
    return float(np.linalg.norm(p1 - p2))


def mouth_aspect_ratio(landmarks: np.ndarray) -> float:
    """
    Compute the Mouth Aspect Ratio.

    Parameters
    ----------
    landmarks : (N, 2) array of (x, y) pixel coordinates.

    Returns
    -------
    mar : float  (small when mouth closed, large when yawning)
    """
    p = landmarks[MOUTH_INDICES]        # shape (8, 2)

    # Three vertical distances
    v1 = _euclidean(p[1], p[7])        # upper-left ↔ lower-left
    v2 = _euclidean(p[2], p[6])        # upper-center ↔ lower-center
    v3 = _euclidean(p[3], p[5])        # upper-right ↔ lower-right

    # Horizontal distance (mouth width)
    h  = _euclidean(p[0], p[4])        # left corner ↔ right corner

    if h < 1e-6:
        return 0.0

    return (v1 + v2 + v3) / (2.0 * h)
