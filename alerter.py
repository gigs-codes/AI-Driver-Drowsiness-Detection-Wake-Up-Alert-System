"""
alerter.py
----------
Smart three-level alert system.

Level 1 (risk ≥ 0.40): soft visual + voice "Please focus"
Level 2 (risk ≥ 0.65): amber visual + voice "Stay alert"
Level 3 (risk ≥ 0.85): red flash  + voice "Wake up"

Voice alerts are delivered via pyttsx3 in a daemon thread so they never
block the video loop. A cooldown prevents the same level from firing
more than once every ALERT_COOLDOWN_SECONDS.
"""

import time
import threading
import logging
from dataclasses import dataclass, field
from typing import Optional

import config as cfg

log = logging.getLogger(__name__)

# Try to initialise pyttsx3; fall back gracefully if it is unavailable.
try:
    import pyttsx3
    _TTS_AVAILABLE = True
except Exception:
    _TTS_AVAILABLE = False
    log.warning("pyttsx3 unavailable — voice alerts disabled.")


# ---------------------------------------------------------------------------
# Alert level definitions
# ---------------------------------------------------------------------------

@dataclass
class AlertLevel:
    level:   int
    label:   str
    message: str
    color_bgr: tuple          # OpenCV BGR
    threshold: float


ALERT_LEVELS = [
    AlertLevel(3, "CRITICAL", "Wake up!",     (0,   0, 255), cfg.ALERT_LEVEL_3),
    AlertLevel(2, "WARNING",  "Stay alert!",  (0, 165, 255), cfg.ALERT_LEVEL_2),
    AlertLevel(1, "CAUTION",  "Please focus", (0, 200, 255), cfg.ALERT_LEVEL_1),
]

NO_ALERT = AlertLevel(0, "OK", "", (0, 200, 80), 0.0)


# ---------------------------------------------------------------------------
# Alerter class
# ---------------------------------------------------------------------------

@dataclass
class Alerter:
    _last_alert_time: dict = field(default_factory=dict)  # level → timestamp
    _tts_engine: Optional[object] = field(default=None, init=False)
    _tts_lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self):
        if _TTS_AVAILABLE:
            try:
                self._tts_engine = pyttsx3.init()
                self._tts_engine.setProperty("rate", 165)
                self._tts_engine.setProperty("volume", 1.0)
            except Exception as exc:
                log.warning("TTS engine init failed: %s", exc)
                self._tts_engine = None

    # ------------------------------------------------------------------
    def evaluate(self, risk: float) -> AlertLevel:
        """
        Evaluate the current risk score, fire voice alert if needed,
        and return the active AlertLevel (or NO_ALERT).
        """
        active = NO_ALERT
        for al in ALERT_LEVELS:
            if risk >= al.threshold:
                active = al
                break

        if active.level > 0:
            self._maybe_speak(active)

        return active

    # ------------------------------------------------------------------
    def _maybe_speak(self, al: AlertLevel) -> None:
        """Fire a voice alert if the cooldown has elapsed."""
        now  = time.time()
        last = self._last_alert_time.get(al.level, 0.0)

        if now - last < cfg.ALERT_COOLDOWN_SECONDS:
            return

        self._last_alert_time[al.level] = now
        self._speak_async(al.message)

    # ------------------------------------------------------------------
    def _speak_async(self, text: str) -> None:
        """Run TTS in a daemon thread to avoid blocking the video loop."""
        if self._tts_engine is None:
            return

        def _run():
            with self._tts_lock:
                try:
                    self._tts_engine.say(text)
                    self._tts_engine.runAndWait()
                except Exception as exc:
                    log.debug("TTS speak error: %s", exc)

        t = threading.Thread(target=_run, daemon=True)
        t.start()
