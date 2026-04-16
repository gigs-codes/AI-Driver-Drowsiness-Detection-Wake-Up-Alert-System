"""
dashboard.py — Session logger + live matplotlib dashboard for DrowsGuard.

Provides:
  SessionLogger  → writes per-frame stats to JSON + CSV
  LiveDashboard  → matplotlib real-time plot (runs in separate thread)
"""

import os
import csv
import json
import time
import logging
import threading
from collections import deque
from typing import Deque, Dict, Any

import config as cfg

logger = logging.getLogger(__name__)

# Optional matplotlib import
try:
    import matplotlib
    matplotlib.use("TkAgg")   # Non-interactive backend friendly with threads
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    logger.warning("matplotlib not found — live dashboard disabled.")


# ─────────────────────────────────────────────
#  Session Logger
# ─────────────────────────────────────────────
class SessionLogger:
    """
    Appends per-frame metrics to a CSV and builds a summary JSON.
    """

    _CSV_FIELDS = [
        "timestamp", "ear", "mar", "pitch", "yaw",
        "fatigue_score", "alert_level",
        "eye_score", "yawn_score", "head_score", "distraction_score",
        "blinks_per_min",
    ]

    def __init__(self, session_id: str | None = None):
        os.makedirs(cfg.LOG_DIR, exist_ok=True)
        if session_id is None:
            session_id = time.strftime("%Y%m%d_%H%M%S")
        self.session_id = session_id
        self._csv_path  = os.path.join(cfg.LOG_DIR, f"session_{session_id}.csv")
        self._json_path = cfg.DASHBOARD_DB

        self._csv_file = open(self._csv_path, "w", newline="")
        self._writer   = csv.DictWriter(self._csv_file, fieldnames=self._CSV_FIELDS)
        self._writer.writeheader()

        self._start_time    = time.monotonic()
        self._frame_count   = 0
        self._alert_count   = 0
        self._peak_risk     = 0.0
        self._total_risk    = 0.0

    def log_frame(self, result) -> None:
        """Log one FrameResult."""
        if not result.face_detected:
            return

        self._frame_count += 1
        self._total_risk  += result.fatigue_score
        self._peak_risk    = max(self._peak_risk, result.fatigue_score)
        if result.alert_level > 0:
            self._alert_count += 1

        row = {
            "timestamp":          round(time.monotonic() - self._start_time, 3),
            "ear":                round(result.ear, 4),
            "mar":                round(result.mar, 4),
            "pitch":              round(result.pitch, 2),
            "yaw":                round(result.yaw,   2),
            "fatigue_score":      round(result.fatigue_score, 4),
            "alert_level":        result.alert_level,
            "eye_score":          round(result.eye_score, 4),
            "yawn_score":         round(result.yawn_score, 4),
            "head_score":         round(result.head_score, 4),
            "distraction_score":  round(result.distraction_score, 4),
            "blinks_per_min":     round(result.blinks_per_min, 2),
        }
        self._writer.writerow(row)

    def close(self) -> Dict[str, Any]:
        """Flush, close, and return session summary dict."""
        self._csv_file.close()
        elapsed = time.monotonic() - self._start_time
        avg_risk = self._total_risk / max(self._frame_count, 1)

        summary = {
            "session_id":       self.session_id,
            "duration_sec":     round(elapsed, 1),
            "total_frames":     self._frame_count,
            "total_alerts":     self._alert_count,
            "peak_risk":        round(self._peak_risk, 4),
            "avg_risk":         round(avg_risk, 4),
            "alert_rate_pct":   round(100 * self._alert_count / max(self._frame_count, 1), 2),
            "csv_path":         self._csv_path,
        }

        # Append to rolling dashboard DB
        db: list = []
        if os.path.exists(self._json_path):
            try:
                with open(self._json_path) as f:
                    db = json.load(f)
            except json.JSONDecodeError:
                db = []
        db.append(summary)
        with open(self._json_path, "w") as f:
            json.dump(db, f, indent=2)

        logger.info("Session saved: %s", summary)
        return summary

    def print_summary(self, summary: Dict[str, Any]) -> None:
        print("\n" + "=" * 55)
        print("  DrowsGuard — Session Summary")
        print("=" * 55)
        print(f"  Session ID   : {summary['session_id']}")
        print(f"  Duration     : {summary['duration_sec']:.1f}s")
        print(f"  Total frames : {summary['total_frames']}")
        print(f"  Total alerts : {summary['total_alerts']}")
        print(f"  Alert rate   : {summary['alert_rate_pct']}%")
        print(f"  Peak risk    : {summary['peak_risk']:.3f}")
        print(f"  Average risk : {summary['avg_risk']:.3f}")
        print(f"  CSV saved to : {summary['csv_path']}")
        print("=" * 55 + "\n")


# ─────────────────────────────────────────────
#  Live Dashboard (matplotlib)
# ─────────────────────────────────────────────
WINDOW_SEC = cfg.HISTORY_WINDOW_SEC


class LiveDashboard:
    """
    Real-time rolling-window matplotlib chart.
    Runs in a background thread to avoid blocking the main camera loop.
    """

    def __init__(self):
        if not HAS_MPL:
            self._active = False
            return
        self._active = True

        # Rolling buffers
        buf = int(WINDOW_SEC * cfg.TARGET_FPS)
        self._t:      Deque[float] = deque(maxlen=buf)
        self._risk:   Deque[float] = deque(maxlen=buf)
        self._eye:    Deque[float] = deque(maxlen=buf)
        self._yawn:   Deque[float] = deque(maxlen=buf)
        self._head:   Deque[float] = deque(maxlen=buf)
        self._lock    = threading.Lock()
        self._start_t = time.monotonic()

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def push(self, result) -> None:
        if not self._active or not result.face_detected:
            return
        t = time.monotonic() - self._start_t
        with self._lock:
            self._t.append(t)
            self._risk.append(result.fatigue_score)
            self._eye.append(result.eye_score)
            self._yawn.append(result.yawn_score)
            self._head.append(result.head_score)

    def _run(self):
        fig, axes = plt.subplots(2, 1, figsize=(9, 5), facecolor="#0d0d0d")
        fig.canvas.manager.set_window_title("DrowsGuard — Live Dashboard")
        ax_risk, ax_comp = axes

        for ax in axes:
            ax.set_facecolor("#1a1a2e")
            ax.tick_params(colors="#aaaaaa")
            for spine in ax.spines.values():
                spine.set_edgecolor("#333355")

        ax_risk.set_ylim(-0.05, 1.05)
        ax_risk.set_ylabel("Fatigue Risk", color="#eeeeee")
        ax_risk.axhline(cfg.RISK_LEVEL1, color="#ffdd44", lw=0.8, ls="--", alpha=0.7)
        ax_risk.axhline(cfg.RISK_LEVEL2, color="#ff8822", lw=0.8, ls="--", alpha=0.7)
        ax_risk.axhline(cfg.RISK_LEVEL3, color="#ff2244", lw=0.8, ls="--", alpha=0.7)

        ax_comp.set_ylim(-0.05, 1.05)
        ax_comp.set_ylabel("Components", color="#eeeeee")
        ax_comp.set_xlabel("Time (s)", color="#eeeeee")

        line_risk,  = ax_risk.plot([], [], color="#00e5ff",  lw=1.5, label="Risk")
        line_eye,   = ax_comp.plot([], [], color="#44ff88",  lw=1.0, label="Eye")
        line_yawn,  = ax_comp.plot([], [], color="#4488ff",  lw=1.0, label="Yawn")
        line_head,  = ax_comp.plot([], [], color="#ffaa44",  lw=1.0, label="Head")

        ax_risk.legend(loc="upper left", facecolor="#111", labelcolor="w", fontsize=8)
        ax_comp.legend(loc="upper left", facecolor="#111", labelcolor="w", fontsize=8)
        plt.tight_layout()

        def _animate(_):
            with self._lock:
                ts    = list(self._t)
                risks = list(self._risk)
                eyes  = list(self._eye)
                yawns = list(self._yawn)
                heads = list(self._head)

            if not ts:
                return line_risk, line_eye, line_yawn, line_head

            t_min = ts[-1] - WINDOW_SEC
            for ax in axes:
                ax.set_xlim(t_min, ts[-1] + 1)

            line_risk.set_data(ts, risks)
            line_eye.set_data( ts, eyes)
            line_yawn.set_data(ts, yawns)
            line_head.set_data(ts, heads)
            return line_risk, line_eye, line_yawn, line_head

        ani = animation.FuncAnimation(   # noqa: F841
            fig, _animate,
            interval=cfg.DASHBOARD_REFRESH_MS,
            blit=True,
        )
        plt.show()
