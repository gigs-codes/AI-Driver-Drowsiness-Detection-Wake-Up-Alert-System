"""
utils/head_pose.py
Estimates head rotation (pitch / yaw / roll) using OpenCV solvePnP
against a generic 3-D facial model.

Returns angles in degrees:
  pitch > 0 → looking up    | pitch < 0 → nodding down
  yaw   > 0 → turning right | yaw   < 0 → turning left
  roll  > 0 → tilting right | roll  < 0 → tilting left
"""

import cv2
import numpy as np
from typing import Tuple, Optional

# 3-D model points (generic face, unit = mm, origin at nose tip)
_MODEL_POINTS_3D = np.array([
    (0.0,     0.0,    0.0),    # Nose tip        [1]
    (0.0,    -63.6, -12.5),    # Chin            [152]
    (-43.3,   32.7, -26.0),    # Left eye corner [33]
    (43.3,    32.7, -26.0),    # Right eye corner [263]
    (-28.9,  -28.9, -24.1),    # Left mouth      [61]
    (28.9,   -28.9, -24.1),    # Right mouth     [291]
], dtype=np.float64)

_HEAD_POSE_INDICES = [1, 152, 33, 263, 61, 291]


def _build_camera_matrix(frame_width: int, frame_height: int) -> np.ndarray:
    focal = frame_width
    cx, cy = frame_width / 2, frame_height / 2
    return np.array([
        [focal, 0,     cx],
        [0,     focal, cy],
        [0,     0,     1 ],
    ], dtype=np.float64)


def estimate_head_pose(
    landmarks_2d: np.ndarray,
    frame_width: int,
    frame_height: int,
) -> Optional[Tuple[float, float, float]]:
    """
    Parameters
    ----------
    landmarks_2d : (N, 2) pixel coordinates of all face-mesh landmarks.
    frame_width, frame_height : camera resolution.

    Returns
    -------
    (pitch, yaw, roll) in degrees, or None if solvePnP fails.
    """
    image_points = landmarks_2d[_HEAD_POSE_INDICES].astype(np.float64)
    camera_matrix = _build_camera_matrix(frame_width, frame_height)
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vec, _ = cv2.solvePnP(
        _MODEL_POINTS_3D,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    if not success:
        return None

    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    # Decompose into Euler angles
    sy = np.sqrt(rotation_mat[0, 0] ** 2 + rotation_mat[1, 0] ** 2)
    singular = sy < 1e-6

    if not singular:
        roll  = np.degrees(np.arctan2( rotation_mat[2, 1], rotation_mat[2, 2]))
        pitch = np.degrees(np.arctan2(-rotation_mat[2, 0], sy))
        yaw   = np.degrees(np.arctan2( rotation_mat[1, 0], rotation_mat[0, 0]))
    else:
        roll  = np.degrees(np.arctan2(-rotation_mat[1, 2], rotation_mat[1, 1]))
        pitch = np.degrees(np.arctan2(-rotation_mat[2, 0], sy))
        yaw   = 0.0

    return float(pitch), float(yaw), float(roll)


def is_head_nodding(pitch: float, pitch_threshold: float) -> bool:
    """Chin dropped — pitch is strongly negative."""
    return pitch < -abs(pitch_threshold)


def is_looking_away(yaw: float, yaw_threshold: float) -> bool:
    """Head turned beyond yaw_threshold degrees."""
    return abs(yaw) > yaw_threshold
