"""
tests/test_detection.py — Unit tests for DrowsGuard detection utilities
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

from utils.ear_calculator import eye_aspect_ratio, both_eyes_ear, is_eye_closed
from utils.mar_calculator import mouth_aspect_ratio, is_yawning
from utils.fatigue_score  import FatigueScoreCalculator, BlinkTracker, DurationTimer
import config as cfg


# ─────────────────────────────────────────────
#  EAR Tests
# ─────────────────────────────────────────────
def _make_open_eye_landmarks() -> np.ndarray:
    """Synthetic open-eye landmark array — EAR ≈ 0.30."""
    # 500 dummy landmarks, eye points at known positions
    lm = np.zeros((500, 2), dtype=np.float32)
    # Standard 6-point eye layout for an open eye
    # p1=outer, p4=inner, p2/p3 upper, p5/p6 lower
    # Width=100, height=30 → EAR = (30+30)/(2*100) = 0.30
    lm[33]  = (0,   0)    # outer corner
    lm[160] = (33,  15)   # upper-1
    lm[158] = (66,  15)   # upper-2
    lm[133] = (100,  0)   # inner corner
    lm[153] = (66, -15)   # lower-2
    lm[144] = (33, -15)   # lower-1
    return lm


def _make_closed_eye_landmarks() -> np.ndarray:
    """Synthetic closed-eye landmark array — EAR ≈ 0.02."""
    lm = np.zeros((500, 2), dtype=np.float32)
    lm[33]  = (0,  0)
    lm[160] = (33, 1)
    lm[158] = (66, 1)
    lm[133] = (100, 0)
    lm[153] = (66, -1)
    lm[144] = (33, -1)
    return lm


def test_ear_open_eye():
    lm = _make_open_eye_landmarks()
    ear = eye_aspect_ratio(lm, cfg.RIGHT_EYE)
    assert 0.25 < ear < 0.40, f"Expected open-eye EAR ~0.30, got {ear:.4f}"


def test_ear_closed_eye():
    lm = _make_closed_eye_landmarks()
    ear = eye_aspect_ratio(lm, cfg.RIGHT_EYE)
    assert ear < 0.10, f"Expected near-zero EAR for closed eye, got {ear:.4f}"


def test_is_eye_closed_flag():
    lm_open   = _make_open_eye_landmarks()
    lm_closed = _make_closed_eye_landmarks()
    assert not is_eye_closed(eye_aspect_ratio(lm_open,   cfg.RIGHT_EYE), cfg.EAR_THRESHOLD)
    assert     is_eye_closed(eye_aspect_ratio(lm_closed, cfg.RIGHT_EYE), cfg.EAR_THRESHOLD)


def test_ear_wrong_index_count():
    lm = np.zeros((500, 2))
    with pytest.raises(ValueError):
        eye_aspect_ratio(lm, [0, 1, 2])   # only 3 indices


# ─────────────────────────────────────────────
#  MAR Tests
# ─────────────────────────────────────────────
def _make_mouth_landmarks(open_ratio: float) -> np.ndarray:
    """Create synthetic mouth landmarks with a given vertical/horizontal ratio."""
    lm = np.zeros((500, 2), dtype=np.float32)
    width = 100.0
    height = open_ratio * width
    # [left, right, top, bottom, top2, bottom2]
    lm[61]  = (0,          0)
    lm[291] = (width,      0)
    lm[0]   = (width / 2,  height / 2)
    lm[17]  = (width / 2, -height / 2)
    lm[267] = (width * 0.7, height * 0.4)
    lm[37]  = (width * 0.7, -height * 0.4)
    return lm


def test_mar_closed_mouth():
    lm = _make_mouth_landmarks(0.05)
    mar = mouth_aspect_ratio(lm, cfg.MOUTH_OUTER)
    assert mar < cfg.MAR_THRESHOLD, f"Should be closed, got MAR={mar:.3f}"


def test_mar_yawning():
    lm = _make_mouth_landmarks(0.8)
    mar = mouth_aspect_ratio(lm, cfg.MOUTH_OUTER)
    assert is_yawning(mar, cfg.MAR_THRESHOLD), f"Should detect yawn, got MAR={mar:.3f}"


# ─────────────────────────────────────────────
#  Fatigue Score Tests
# ─────────────────────────────────────────────
def test_fatigue_zero_on_alert_state():
    calc = FatigueScoreCalculator()
    score = calc.update(
        ear=0.35, eye_closed=False, mar=0.2, yawning=False,
        head_nodding=False, looking_away=False
    )
    assert score == 0.0, "No alerts should produce zero fatigue score"


def test_fatigue_rises_on_closed_eyes(monkeypatch):
    """Simulate several seconds of closed eyes and check score rises."""
    import time as _time
    calc = FatigueScoreCalculator()

    # Patch monotonic to simulate 3 seconds passing
    _start = _time.monotonic()

    def fake_monotonic():
        return _start + 3.0

    monkeypatch.setattr("utils.fatigue_score.time.monotonic", fake_monotonic)
    score = calc.update(
        ear=0.10, eye_closed=True, mar=0.1, yawning=False,
        head_nodding=False, looking_away=False
    )
    assert score > 0.0, "Score should be > 0 after simulated eye closure"


def test_alert_level_thresholds():
    calc = FatigueScoreCalculator()
    # Inject raw_risk directly
    calc._ema_risk = cfg.RISK_LEVEL1 + 0.01
    assert calc.alert_level() == 1

    calc._ema_risk = cfg.RISK_LEVEL2 + 0.01
    assert calc.alert_level() == 2

    calc._ema_risk = cfg.RISK_LEVEL3 + 0.01
    assert calc.alert_level() == 3

    calc._ema_risk = 0.0
    assert calc.alert_level() == 0


# ─────────────────────────────────────────────
#  Blink Tracker Tests
# ─────────────────────────────────────────────
def test_blink_tracker_counts_blinks():
    bt = BlinkTracker()
    # Simulate 5 blink transitions
    for _ in range(5):
        bt.update(True)   # eye closes
        bt.update(False)  # eye opens

    assert bt.blinks_per_minute > 0


def test_blink_tracker_no_false_positive():
    bt = BlinkTracker()
    bt.update(False)
    bt.update(False)
    bt.update(False)
    # All open — no blink
    assert len(bt._blink_times) == 0


# ─────────────────────────────────────────────
#  Duration Timer Tests
# ─────────────────────────────────────────────
def test_duration_timer_resets_on_false():
    dt = DurationTimer()
    # When condition is False, duration should be 0
    assert dt.update(False) == 0.0


def test_duration_timer_tracks_true():
    import time
    dt = DurationTimer()
    dt.update(True)
    time.sleep(0.05)
    elapsed = dt.update(True)
    assert elapsed > 0.01
