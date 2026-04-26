"""
tests/test_detection.py
-----------------------
Pytest tests for DrowsGuard core logic.

Run:
    pip install pytest
    pytest tests/ -v
"""

import sys
import os

import numpy as np
import pytest

# Make the project root importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.ear_calculator import eye_aspect_ratio, compute_average_ear, RIGHT_EYE_INDICES, LEFT_EYE_INDICES
from utils.mar_calculator import mouth_aspect_ratio
from utils.fatigue_score  import (
    FatigueState, FatigueComponents,
    eye_closure_score, yawn_score, head_pose_score,
    compute_risk, apply_ema, update_fatigue,
)
import config as cfg


# ---------------------------------------------------------------------------
# Helpers — synthetic landmark arrays
# ---------------------------------------------------------------------------

def _make_open_eye_landmarks() -> np.ndarray:
    """
    Return a minimal (500, 2) landmark array representing OPEN eyes.
    EAR for open eye ≈ 0.30 (h=20, v1=v2=6).
    """
    lm = np.zeros((500, 2), dtype=np.float64)

    # Right eye (indices 33, 160, 158, 133, 153, 144)
    # p1=outer, p2=upper1, p3=upper2, p4=inner, p5=lower1, p6=lower2
    #   outer corner at (0, 10)
    #   inner corner at (20, 10)
    #   vertical spread = 6 pixels
    re = RIGHT_EYE_INDICES
    lm[re[0]] = [0,  10]   # outer
    lm[re[1]] = [5,  7]    # upper1
    lm[re[2]] = [15, 7]    # upper2
    lm[re[3]] = [20, 10]   # inner
    lm[re[4]] = [15, 13]   # lower1
    lm[re[5]] = [5,  13]   # lower2

    # Mirror for left eye
    le = LEFT_EYE_INDICES
    lm[le[0]] = [30, 10]
    lm[le[1]] = [35, 7]
    lm[le[2]] = [45, 7]
    lm[le[3]] = [50, 10]
    lm[le[4]] = [45, 13]
    lm[le[5]] = [35, 13]

    return lm


def _make_closed_eye_landmarks() -> np.ndarray:
    """Closed eyes — upper and lower lids at the same y → EAR ≈ 0."""
    lm = _make_open_eye_landmarks().copy()
    re = RIGHT_EYE_INDICES
    lm[re[1]][1] = 10   # upper1 → same as corners
    lm[re[2]][1] = 10
    lm[re[4]][1] = 10
    lm[re[5]][1] = 10

    le = LEFT_EYE_INDICES
    lm[le[1]][1] = 10
    lm[le[2]][1] = 10
    lm[le[4]][1] = 10
    lm[le[5]][1] = 10
    return lm


def _make_closed_mouth_landmarks() -> np.ndarray:
    """
    Mouth tightly closed — very small vertical gap (1 px) relative to a wide
    horizontal span (100 px), giving MAR ≈ 0.03 which is well below threshold.
    """
    from utils.mar_calculator import MOUTH_INDICES
    lm = np.zeros((500, 2), dtype=np.float64)
    # Corners (horizontal reference)
    lm[MOUTH_INDICES[0]] = [0,   100]   # left corner
    lm[MOUTH_INDICES[4]] = [100, 100]   # right corner
    # Upper lip — barely above y=100
    lm[MOUTH_INDICES[1]] = [25,  99]
    lm[MOUTH_INDICES[2]] = [50,  99]
    lm[MOUTH_INDICES[3]] = [75,  99]
    # Lower lip — barely below y=100
    lm[MOUTH_INDICES[5]] = [75,  101]
    lm[MOUTH_INDICES[6]] = [50,  101]
    lm[MOUTH_INDICES[7]] = [25,  101]
    return lm


def _make_open_mouth_landmarks() -> np.ndarray:
    """Mouth wide open — large vertical spread → MAR > threshold."""
    from utils.mar_calculator import MOUTH_INDICES
    lm = np.zeros((500, 2), dtype=np.float64)
    lm[MOUTH_INDICES[0]] = [0,   100]    # left corner
    lm[MOUTH_INDICES[1]] = [25,  75]     # upper-left  (large v gap)
    lm[MOUTH_INDICES[2]] = [50,  65]     # upper-center
    lm[MOUTH_INDICES[3]] = [75,  75]     # upper-right
    lm[MOUTH_INDICES[4]] = [100, 100]    # right corner
    lm[MOUTH_INDICES[5]] = [75,  125]    # lower-right
    lm[MOUTH_INDICES[6]] = [50,  140]    # lower-center
    lm[MOUTH_INDICES[7]] = [25,  125]    # lower-left
    return lm


# ---------------------------------------------------------------------------
# EAR tests
# ---------------------------------------------------------------------------

class TestEAR:

    def test_open_eyes_ear_above_threshold(self):
        lm  = _make_open_eye_landmarks()
        ear, r, l = compute_average_ear(lm)
        assert ear > cfg.EAR_THRESHOLD, f"Open eyes should give EAR > {cfg.EAR_THRESHOLD}, got {ear:.3f}"

    def test_closed_eyes_ear_near_zero(self):
        lm  = _make_closed_eye_landmarks()
        ear, r, l = compute_average_ear(lm)
        assert ear < 0.05, f"Closed eyes should give EAR ≈ 0, got {ear:.3f}"

    def test_ear_symmetric(self):
        lm  = _make_open_eye_landmarks()
        ear, r, l = compute_average_ear(lm)
        assert abs(r - l) < 0.01, "Symmetric eyes should have equal EAR"

    def test_ear_non_negative(self):
        lm  = _make_open_eye_landmarks()
        ear, r, l = compute_average_ear(lm)
        assert ear >= 0.0

    def test_zero_landmarks_returns_zero(self):
        lm  = np.zeros((500, 2), dtype=np.float64)
        ear, r, l = compute_average_ear(lm)
        assert ear == 0.0


# ---------------------------------------------------------------------------
# MAR tests
# ---------------------------------------------------------------------------

class TestMAR:

    def test_closed_mouth_below_threshold(self):
        lm  = _make_closed_mouth_landmarks()
        mar = mouth_aspect_ratio(lm)
        assert mar < cfg.MAR_THRESHOLD, f"Closed mouth MAR should be < {cfg.MAR_THRESHOLD}, got {mar:.3f}"

    def test_open_mouth_above_threshold(self):
        lm  = _make_open_mouth_landmarks()
        mar = mouth_aspect_ratio(lm)
        assert mar > cfg.MAR_THRESHOLD, f"Open mouth MAR should be > {cfg.MAR_THRESHOLD}, got {mar:.3f}"

    def test_mar_non_negative(self):
        lm  = _make_open_mouth_landmarks()
        mar = mouth_aspect_ratio(lm)
        assert mar >= 0.0

    def test_mar_zero_for_degenerate_input(self):
        lm  = np.zeros((500, 2), dtype=np.float64)
        mar = mouth_aspect_ratio(lm)
        assert mar == 0.0


# ---------------------------------------------------------------------------
# Fatigue score tests
# ---------------------------------------------------------------------------

class TestFatigueScore:

    def test_zero_inputs_give_zero_risk(self):
        c = FatigueComponents(0, 0, 0, 0)
        assert compute_risk(c) == 0.0

    def test_all_one_inputs_give_one_risk(self):
        c = FatigueComponents(1, 1, 1, 1)
        risk = compute_risk(c)
        assert abs(risk - 1.0) < 1e-9

    def test_weights_sum_to_one(self):
        total = (cfg.W_EYE_CLOSURE + cfg.W_YAWN
                 + cfg.W_HEAD_POSE  + cfg.W_DISTRACTION)
        assert abs(total - 1.0) < 1e-9, f"Weights sum = {total}, expected 1.0"

    def test_ema_smoothing_moves_toward_current(self):
        prev = 0.0
        curr = 1.0
        smoothed = apply_ema(curr, prev)
        # With alpha=0.3: 0.3*1.0 + 0.7*0.0 = 0.3
        assert abs(smoothed - cfg.EMA_ALPHA) < 1e-9

    def test_ema_idempotent_on_same_value(self):
        for v in (0.0, 0.5, 1.0):
            assert abs(apply_ema(v, v) - v) < 1e-9

    def test_eye_closure_score_open_eyes(self):
        state = FatigueState()
        score = eye_closure_score(cfg.EAR_THRESHOLD + 0.05, state)
        assert score == 0.0, "Open eyes should yield score 0"

    def test_eye_closure_score_increases_over_frames(self):
        state  = FatigueState()
        ear_closed = cfg.EAR_THRESHOLD - 0.05
        scores = [eye_closure_score(ear_closed, state) for _ in range(20)]
        assert scores[-1] > scores[0], "Score should increase as eye stays closed"

    def test_yawn_score_zero_when_mouth_closed(self):
        state = FatigueState()
        score = yawn_score(cfg.MAR_THRESHOLD - 0.1, state)
        assert score == 0.0

    def test_yawn_score_one_after_consec_frames(self):
        state = FatigueState()
        mar_open = cfg.MAR_THRESHOLD + 0.1
        score = 0.0
        for _ in range(cfg.MAR_CONSEC_FRAMES + 1):
            score = yawn_score(mar_open, state)
        assert score == 1.0

    def test_head_pose_neutral_gives_zero(self):
        score = head_pose_score(0.0, 0.0)
        assert score == 0.0

    def test_head_pose_extreme_gives_one(self):
        score = head_pose_score(cfg.HEAD_PITCH_THRESHOLD * 3, 0.0)
        assert score == 1.0

    def test_head_pose_none_gives_zero(self):
        score = head_pose_score(None, None)
        assert score == 0.0

    def test_update_fatigue_returns_float_in_range(self):
        state = FatigueState()
        risk  = update_fatigue(0.25, 0.40, 5.0, 3.0, state)
        assert 0.0 <= risk <= 1.0

    def test_update_fatigue_risk_increases_with_closed_eyes(self):
        state   = FatigueState()
        ear_closed = cfg.EAR_THRESHOLD - 0.05

        # Simulate 30 frames of closed eyes
        risks = []
        for _ in range(30):
            r = update_fatigue(ear_closed, 0.0, 0.0, 0.0, state)
            risks.append(r)

        assert risks[-1] > risks[0], "Risk should rise as eyes stay closed"

    def test_risk_resets_when_eyes_open(self):
        state = FatigueState()
        ear_closed = cfg.EAR_THRESHOLD - 0.05
        ear_open   = cfg.EAR_THRESHOLD + 0.05

        for _ in range(30):
            update_fatigue(ear_closed, 0.0, 0.0, 0.0, state)

        risk_high = state.smoothed_risk

        for _ in range(60):
            update_fatigue(ear_open, 0.0, 0.0, 0.0, state)

        risk_low = state.smoothed_risk
        assert risk_low < risk_high, "Risk should decrease after eyes open"


# ---------------------------------------------------------------------------
# Config sanity
# ---------------------------------------------------------------------------

class TestConfig:

    def test_thresholds_in_range(self):
        assert 0 < cfg.EAR_THRESHOLD < 1
        assert 0 < cfg.MAR_THRESHOLD < 2
        assert cfg.ALERT_LEVEL_1 < cfg.ALERT_LEVEL_2 < cfg.ALERT_LEVEL_3 <= 1.0

    def test_alpha_in_range(self):
        assert 0.0 < cfg.EMA_ALPHA < 1.0
