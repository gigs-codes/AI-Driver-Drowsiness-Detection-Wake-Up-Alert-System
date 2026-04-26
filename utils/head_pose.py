"""
utils/head_pose.py
------------------
Estimates head pitch (nodding) and yaw (turning) from MediaPipe landmarks
using OpenCV's solvePnP with a generic 3-D face model.

The 6 landmarks chosen for PnP are the standard "6-point" subset that gives
a stable, well-conditioned pose even on a simple CPU:
  Nose tip        : 1
  Chin            : 152
  Left eye corner : 263
  Right eye corner: 33
  Left mouth      : 287
  Right mouth     : 57
"""

import numpy as np
import cv2
from typing import Tuple, Optional


# ---------------------------------------------------------------------------
# Generic 3-D face model (mm, origin at nose tip)
# ---------------------------------------------------------------------------
FACE_3D_MODEL = np.array([
    [0.0,    0.0,    0.0   ],   # Nose tip
    [0.0,   -330.0, -65.0  ],   # Chin
    [-225.0,  170.0,-135.0 ],   # Left eye left corner
    [ 225.0,  170.0,-135.0 ],   # Right eye right corner
    [-150.0, -150.0,-125.0 ],   # Left mouth corner
    [ 150.0, -150.0,-125.0 ],   # Right mouth corner
], dtype=np.float64)

# Corresponding MediaPipe landmark indices
POSE_LANDMARK_IDS = [1, 152, 263, 33, 287, 57]

# Distortion coefficients — assume no lens distortion for webcam simplicity
DIST_COEFFS = np.zeros((4, 1), dtype=np.float64)


def _build_camera_matrix(frame_w: int, frame_h: int) -> np.ndarray:
    """Approximate intrinsic camera matrix from frame dimensions."""
    focal  = frame_w                              # heuristic focal length
    cx, cy = frame_w / 2.0, frame_h / 2.0
    return np.array([
        [focal,  0.0,   cx],
        [0.0,   focal,  cy],
        [0.0,    0.0,   1.0],
    ], dtype=np.float64)


def estimate_head_pose(
    landmarks: np.ndarray,
    frame_w:   int,
    frame_h:   int,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Estimate head pitch and yaw angles (degrees).

    Parameters
    ----------
    landmarks : (N, 2) array of (x, y) pixel coordinates.
    frame_w   : Frame width in pixels.
    frame_h   : Frame height in pixels.

    Returns
    -------
    (pitch, yaw) in degrees, or (None, None) if solvePnP fails.
      pitch > 0  → head tilted forward (drowsy nod)
      yaw   > 0  → head turned right
    """
    image_points = landmarks[POSE_LANDMARK_IDS].astype(np.float64)
    cam_matrix   = _build_camera_matrix(frame_w, frame_h)

    success, rot_vec, _ = cv2.solvePnP(
        FACE_3D_MODEL,
        image_points,
        cam_matrix,
        DIST_COEFFS,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return None, None

    # Convert rotation vector → rotation matrix → Euler angles
    rot_mat, _ = cv2.Rodrigues(rot_vec)

    # Decompose via RQDecomp3x3 — returns angles in degrees
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rot_mat)
    pitch = angles[0]   # Nodding (X-axis rotation)
    yaw   = angles[1]   # Turning (Y-axis rotation)

    return float(pitch), float(yaw)
