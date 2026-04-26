"""
utils/fatigue_score.py
Computes a [0, 1] fatigue / drowsiness risk score using the formula:

  Risk = 0.5·EyeClosure + 0.2·Yawn + 0.2·HeadPose + 0.1·Distraction

Each component is also normalised to [0, 1] before weighting.
Also tracks blink rate (blinks per minute) to detect microsleep.
"""

import time
from collections import deque
from typing import Deque

import config as cfg


class BlinkTracker:
    """Counts blinks in a rolling 60-second window."""

    def __init__(self, window_sec: int = 60):
        self._window = window_sec
        self._blink_times: Deque[float] = deque()
        self._eye_was_closed: bool = False

    def update(self, eye_closed: bool) -> None:
        now = time.monotonic()
        # Rising edge detection (open→closed transition = one blink)
        if eye_closed and not self._eye_was_closed:
            self._blink_times.append(now)
        self._eye_was_closed = eye_closed

        # Drop stale blinks
        cutoff = now - self._window
        while self._blink_times and self._blink_times[0] < cutoff:
            self._blink_times.popleft()

    @property
    def blinks_per_minute(self) -> float:
        if not self._blink_times:
            return 0.0
        elapsed = max(time.monotonic() - self._blink_times[0], 1.0)
        return len(self._blink_times) / elapsed * 60.0


class DurationTimer:
    """Measures continuous seconds a condition has been True."""

    def __init__(self):
        self._start: float | None = None

    def update(self, condition: bool) -> float:
        if condition:
            if self._start is None:
                self._start = time.monotonic()
            return time.monotonic() - self._start
        else:
            self._start = None
            return 0.0


class FatigueScoreCalculator:
    """
    Stateful calculator that accumulates per-frame signals and
    returns a rolling fatigue risk score in [0, 1].
    """

    def __init__(self):
        self.blink_tracker     = BlinkTracker()
        self._eye_timer        = DurationTimer()
        self._yawn_timer       = DurationTimer()
        self._head_down_timer  = DurationTimer()
        self._look_away_timer  = DurationTimer()

        # Exponential moving average for smoothing
        self._ema_risk: float = 0.0
        self._alpha: float    = 0.3   # EMA smoothing factor

        # Component scores (exposed for dashboard)
        self.eye_score         = 0.0
        self.yawn_score        = 0.0
        self.head_pose_score   = 0.0
        self.distraction_score = 0.0
        self.raw_risk          = 0.0

    # ──────────────────────────────────────────
    def update(
        self,
        ear: float,
        eye_closed: bool,
        mar: float,
        yawning: bool,
        head_nodding: bool,
        looking_away: bool,
    ) -> float:
        """
        Call once per frame.  Returns smoothed risk in [0, 1].
        """
        # ── Blink tracker
        self.blink_tracker.update(eye_closed)

        # ── Durations
        eye_dur  = self._eye_timer.update(eye_closed)
        yawn_dur = self._yawn_timer.update(yawning)
        head_dur = self._head_down_timer.update(head_nodding)
        away_dur = self._look_away_timer.update(looking_away)

        # ── Eye closure score  (duration / threshold, capped at 1)
        self.eye_score = min(eye_dur / cfg.EYE_CLOSE_CONSECUTIVE, 1.0)

        # ── Yawn score
        self.yawn_score = min(yawn_dur / cfg.YAWN_CONSECUTIVE, 1.0)

        # ── Head pose score  (blend nodding + looking-away)
        head_nod_s = min(head_dur / cfg.HEAD_DOWN_CONSECUTIVE, 1.0)
        look_away_s = min(away_dur / cfg.LOOK_AWAY_CONSECUTIVE, 1.0)
        self.head_pose_score = max(head_nod_s, look_away_s)

        # ── Distraction (low blink rate)
        bpm = self.blink_tracker.blinks_per_minute
        if bpm < cfg.BLINK_RATE_LOW and bpm > 0:
            self.distraction_score = min(
                (cfg.BLINK_RATE_LOW - bpm) / cfg.BLINK_RATE_LOW, 1.0
            )
        else:
            self.distraction_score = 0.0

        # ── Weighted sum
        self.raw_risk = (
            cfg.W_EYE_CLOSURE * self.eye_score
            + cfg.W_YAWN      * self.yawn_score
            + cfg.W_HEAD_POSE * self.head_pose_score
            + cfg.W_DISTRACTION * self.distraction_score
        )

        # ── EMA smoothing
        self._ema_risk = self._alpha * self.raw_risk + (1 - self._alpha) * self._ema_risk
        return float(self._ema_risk)

    @property
    def smoothed_risk(self) -> float:
        return self._ema_risk

    def alert_level(self) -> int:
        """Returns 0 (safe) | 1 (mild) | 2 (dangerous) | 3 (critical)."""
        r = self._ema_risk
        if r >= cfg.RISK_LEVEL3:
            return 3
        if r >= cfg.RISK_LEVEL2:
            return 2
        if r >= cfg.RISK_LEVEL1:
            return 1
        return 0
