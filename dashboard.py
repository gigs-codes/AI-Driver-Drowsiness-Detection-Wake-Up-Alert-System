"""
dashboard.py
------------
Real-time matplotlib dashboard rendered in a separate window.

Plots:
  • Fatigue risk score over the last N seconds (rolling window)
  • EAR and MAR over time
  • Horizontal threshold lines for each alert level

Runs in the MAIN thread via non-blocking plt.pause().
Call update() once per frame; the window only redraws when enough time has
elapsed (DASHBOARD_UPDATE_INTERVAL) to avoid degrading FPS.
"""

import time
import collections
from typing import Deque

import numpy as np
import matplotlib
matplotlib.use("TkAgg")          # works headless-ish; falls back safely
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import config as cfg
from detector import FrameResult


class Dashboard:
    """
    Non-blocking matplotlib dashboard.

    Usage
    -----
    dash = Dashboard()
    # inside webcam loop:
    dash.update(result, fps)
    # on exit:
    dash.close()
    """

    def __init__(self):
        max_pts = int(cfg.DASHBOARD_HISTORY_SECONDS / (1.0 / cfg.TARGET_FPS))

        self._times: Deque[float] = collections.deque(maxlen=max_pts)
        self._risk:  Deque[float] = collections.deque(maxlen=max_pts)
        self._ear:   Deque[float] = collections.deque(maxlen=max_pts)
        self._mar:   Deque[float] = collections.deque(maxlen=max_pts)

        self._start_time   = time.time()
        self._last_redraw  = 0.0

        self._setup_figure()

    # ------------------------------------------------------------------
    def _setup_figure(self) -> None:
        plt.ion()
        self._fig, axes = plt.subplots(
            2, 1, figsize=(9, 5),
            facecolor="#0f0f1a",
            gridspec_kw={"hspace": 0.45},
        )
        self._fig.canvas.manager.set_window_title("DrowsGuard — Live Dashboard")

        # ── Risk axes ──────────────────────────────────────────────────
        ax_risk = axes[0]
        ax_risk.set_facecolor("#14141f")
        ax_risk.set_title("Fatigue Risk Score", color="#c8c8e8", fontsize=10)
        ax_risk.set_ylim(0, 1.05)
        ax_risk.set_ylabel("Risk", color="#8888a8")
        ax_risk.tick_params(colors="#8888a8")
        for spine in ax_risk.spines.values():
            spine.set_edgecolor("#2a2a3a")

        # Threshold lines
        ax_risk.axhline(cfg.ALERT_LEVEL_1, color="#00c8ff", lw=0.8, ls="--", alpha=0.6, label="L1 caution")
        ax_risk.axhline(cfg.ALERT_LEVEL_2, color="#ffaa00", lw=0.8, ls="--", alpha=0.6, label="L2 warning")
        ax_risk.axhline(cfg.ALERT_LEVEL_3, color="#ff3333", lw=0.8, ls="--", alpha=0.6, label="L3 critical")
        ax_risk.legend(loc="upper right", fontsize=7, framealpha=0.3, labelcolor="#c8c8e8")

        self._line_risk, = ax_risk.plot([], [], lw=1.5, color="#7c6af7")
        self._fill_risk  = None
        self._ax_risk    = ax_risk

        # ── EAR / MAR axes ─────────────────────────────────────────────
        ax_em = axes[1]
        ax_em.set_facecolor("#14141f")
        ax_em.set_title("EAR & MAR", color="#c8c8e8", fontsize=10)
        ax_em.set_ylim(0, 1.0)
        ax_em.set_ylabel("Ratio", color="#8888a8")
        ax_em.set_xlabel("seconds", color="#8888a8")
        ax_em.tick_params(colors="#8888a8")
        for spine in ax_em.spines.values():
            spine.set_edgecolor("#2a2a3a")

        ax_em.axhline(cfg.EAR_THRESHOLD, color="#06d6a0", lw=0.8, ls=":", alpha=0.6, label=f"EAR thr {cfg.EAR_THRESHOLD}")
        ax_em.axhline(cfg.MAR_THRESHOLD, color="#f59e0b", lw=0.8, ls=":", alpha=0.6, label=f"MAR thr {cfg.MAR_THRESHOLD}")
        ax_em.legend(loc="upper right", fontsize=7, framealpha=0.3, labelcolor="#c8c8e8")

        self._line_ear, = ax_em.plot([], [], lw=1.2, color="#06d6a0", label="EAR")
        self._line_mar, = ax_em.plot([], [], lw=1.2, color="#f59e0b", label="MAR")
        self._ax_em     = ax_em

        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.05)

    # ------------------------------------------------------------------
    def update(self, result: FrameResult, fps: float) -> None:
        """
        Feed one frame's result into the rolling buffer.
        Redraws the figure at most every DASHBOARD_UPDATE_INTERVAL seconds.
        """
        t = time.time() - self._start_time
        self._times.append(t)
        self._risk.append(result.risk)
        self._ear.append(result.ear)
        self._mar.append(result.mar)

        now = time.time()
        if now - self._last_redraw < cfg.DASHBOARD_UPDATE_INTERVAL:
            return
        self._last_redraw = now
        self._redraw(fps)

    # ------------------------------------------------------------------
    def _redraw(self, fps: float) -> None:
        if not plt.fignum_exists(self._fig.number):
            return

        t_arr    = np.array(self._times)
        risk_arr = np.array(self._risk)
        ear_arr  = np.array(self._ear)
        mar_arr  = np.array(self._mar)

        # ── Risk line + fill ───────────────────────────────────────────
        self._line_risk.set_data(t_arr, risk_arr)
        if self._fill_risk is not None:
            self._fill_risk.remove()
        self._fill_risk = self._ax_risk.fill_between(
            t_arr, risk_arr, alpha=0.15, color="#7c6af7"
        )
        self._ax_risk.set_xlim(
            max(0, t_arr[-1] - cfg.DASHBOARD_HISTORY_SECONDS) if len(t_arr) else 0,
            (t_arr[-1] + 1) if len(t_arr) else cfg.DASHBOARD_HISTORY_SECONDS,
        )

        # FPS in title
        self._ax_risk.set_title(
            f"Fatigue Risk Score  ({fps:.0f} FPS)", color="#c8c8e8", fontsize=10
        )

        # ── EAR / MAR lines ────────────────────────────────────────────
        self._line_ear.set_data(t_arr, ear_arr)
        self._line_mar.set_data(t_arr, mar_arr)
        self._ax_em.set_xlim(self._ax_risk.get_xlim())

        self._fig.canvas.draw_idle()
        plt.pause(0.001)

    # ------------------------------------------------------------------
    def close(self) -> None:
        plt.ioff()
        plt.close("all")
