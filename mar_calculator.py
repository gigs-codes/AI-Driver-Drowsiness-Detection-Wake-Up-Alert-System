"""
utils/mar_calculator.py
Mouth Aspect Ratio (MAR) — detects yawning from lip landmarks.

MAR = (‖A−D‖ + ‖B−E‖ + ‖C−F‖) / (3 · ‖G−H‖)

where A–F are vertical lip pairs and G, H are the mouth corners.
"""

import numpy as np
from typing import List


def _dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def mouth_aspect_ratio(landmarks: np.ndarray, mouth_indices: List[int]) -> float:
    """
    Compute MAR.

    Parameters
    ----------
    landmarks     : (N, 2) array of (x, y) pixel coordinates.
    mouth_indices : 6-element list
                    [left-corner, right-corner, upper-mid, lower-mid,
                     upper-left, lower-left]
                    MediaPipe defaults: [61, 291, 0, 17, 267, 37]

    Returns
    -------
    mar : float  — 0.0 (closed) … ~1.0+ (wide yawn)
    """
    if len(mouth_indices) < 6:
        raise ValueError("mouth_indices must have at least 6 elements.")

    pts = landmarks[mouth_indices]
    left, right, top, bottom, top2, bottom2 = pts[:6]

    vertical_1 = _dist(top, bottom)
    vertical_2 = _dist(top2, bottom2)
    horizontal = _dist(left, right)

    if horizontal < 1e-6:
        return 0.0

    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def is_yawning(mar: float, threshold: float) -> bool:
    return mar > threshold
