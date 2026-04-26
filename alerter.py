"""
<<<<<<< HEAD
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
=======
alerter.py — Smart 3-level alert system for DrowsGuard
Handles sound, voice, screen flash, and optional remote notifications.
"""

import os
import sys
import time
import threading
import logging
from typing import Optional
from dataclasses import dataclass, field

import config as cfg

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Alert State
# ─────────────────────────────────────────────
@dataclass
class AlertState:
    active_level: int   = 0
    issued_at: float    = 0.0
    response_detected: bool = False
    escalation_count: int   = 0
    total_alerts: int        = 0
    alert_history: list      = field(default_factory=list)


# ─────────────────────────────────────────────
#  Sound helper (pygame preferred, fallback playsound)
# ─────────────────────────────────────────────
def _try_import_audio():
    try:
        import pygame
        pygame.mixer.init()
        return "pygame"
    except ImportError:
        pass
    try:
        from playsound import playsound  # noqa: F401
        return "playsound"
    except ImportError:
        pass
    return None


_AUDIO_BACKEND = _try_import_audio()


def _play_sound(path: str, loop: bool = False) -> Optional[threading.Thread]:
    """Non-blocking sound playback."""
    if not os.path.exists(path):
        logger.warning("Alarm file not found: %s — using beep fallback.", path)
        _beep_fallback()
        return None

    def _play():
        if _AUDIO_BACKEND == "pygame":
            import pygame
            sound = pygame.mixer.Sound(path)
            sound.play(loops=-1 if loop else 0)
        elif _AUDIO_BACKEND == "playsound":
            from playsound import playsound
            playsound(path, block=True)

    t = threading.Thread(target=_play, daemon=True)
    t.start()
    return t


def _stop_sound():
    if _AUDIO_BACKEND == "pygame":
        try:
            import pygame
            pygame.mixer.stop()
        except Exception:
            pass


def _beep_fallback():
    """Cross-platform ASCII bell beep."""
    try:
        import winsound
        winsound.Beep(1000, 500)
    except ImportError:
        print("\a", end="", flush=True)   # UNIX bell


# ─────────────────────────────────────────────
#  Voice helper (pyttsx3 offline TTS)
# ─────────────────────────────────────────────
_tts_engine = None
_tts_lock   = threading.Lock()


def _speak(text: str):
    """Non-blocking offline TTS."""
    def _inner():
        global _tts_engine
        with _tts_lock:
            try:
                import pyttsx3
                if _tts_engine is None:
                    _tts_engine = pyttsx3.init()
                    _tts_engine.setProperty("rate", 160)
                    _tts_engine.setProperty("volume", 1.0)
                _tts_engine.say(text)
                _tts_engine.runAndWait()
            except Exception as e:
                logger.warning("TTS failed: %s", e)
    threading.Thread(target=_inner, daemon=True).start()


# ─────────────────────────────────────────────
#  Optional Twilio / Telegram notification
# ─────────────────────────────────────────────
def _send_remote_alert(message: str, notif_cfg: cfg.NotificationConfig):
    """Fire-and-forget remote notification."""
    def _inner():
        # ── Twilio SMS
        if notif_cfg.twilio_sid and notif_cfg.twilio_token:
            try:
                from twilio.rest import Client
                client = Client(notif_cfg.twilio_sid, notif_cfg.twilio_token)
                client.messages.create(
                    body=message,
                    from_=notif_cfg.twilio_from,
                    to=notif_cfg.alert_phone,
                )
                logger.info("Twilio SMS sent.")
            except Exception as e:
                logger.error("Twilio error: %s", e)

        # ── Telegram
        if notif_cfg.telegram_token and notif_cfg.telegram_chat_id:
            try:
                import requests
                url = f"https://api.telegram.org/bot{notif_cfg.telegram_token}/sendMessage"
                requests.post(url, data={"chat_id": notif_cfg.telegram_chat_id,
                                         "text": message}, timeout=5)
                logger.info("Telegram alert sent.")
            except Exception as e:
                logger.error("Telegram error: %s", e)

    threading.Thread(target=_inner, daemon=True).start()


# ─────────────────────────────────────────────
#  Main Alerter Class
# ─────────────────────────────────────────────
MESSAGES = {
    1: ("Please focus on the road.", "⚠️  MILD FATIGUE"),
    2: ("Wake up! Please stay alert now.", "🚨 DANGEROUS DROWSINESS"),
    3: ("DANGER! Wake up immediately! Pulling over recommended.", "🆘 CRITICAL — NO RESPONSE"),
}


class DrowsinessAlerter:
    """
    Manages alert state machine.
    Call `check(alert_level, attentive)` once per frame.
    """

    def __init__(
        self,
        notif_cfg: Optional[cfg.NotificationConfig] = None,
        sound_path: str = cfg.ALARM_SOUND_PATH,
    ):
        self.notif_cfg  = notif_cfg or cfg.NotificationConfig()
        self.sound_path = sound_path
        self.state      = AlertState()
        self._last_voice_t: float = 0.0
        self._voice_cooldown: float = 8.0

    # ── Public API ──────────────────────────
    def check(self, alert_level: int, attentive: bool) -> AlertState:
        """
        alert_level : 0–3 from FatigueScoreCalculator.alert_level()
        attentive   : True if driver responded (eyes open, head up, etc.)
        """
        now = time.monotonic()

        # Driver became attentive → cancel current alert
        if attentive and self.state.active_level > 0:
            self._cancel_alert()
            return self.state

        # No alert needed
        if alert_level == 0:
            if self.state.active_level > 0:
                self._cancel_alert()
            return self.state

        # Check escalation timeout
        if (
            self.state.active_level > 0
            and not attentive
            and (now - self.state.issued_at) > cfg.ESCALATION_TIMEOUT
            and alert_level >= self.state.active_level
        ):
            new_level = min(self.state.active_level + 1, 3)
            if new_level > self.state.active_level:
                self._trigger(new_level, now, escalated=True)
            return self.state

        # New or higher alert
        if alert_level > self.state.active_level:
            self._trigger(alert_level, now)

        return self.state

    def reset(self):
        self._cancel_alert()
        self.state.escalation_count = 0
        self.state.total_alerts = 0
        self.state.alert_history.clear()

    # ── Internal ────────────────────────────
    def _trigger(self, level: int, now: float, escalated: bool = False):
        voice_msg, label = MESSAGES[level]
        _stop_sound()

        logger.warning("Alert level %d — %s%s", level, label,
                       " [ESCALATED]" if escalated else "")

        # Sound
        loop = level >= 2
        _play_sound(self.sound_path, loop=loop)

        # Voice (with cooldown to avoid spam)
        if (now - self._last_voice_t) > self._voice_cooldown:
            _speak(voice_msg)
            self._last_voice_t = now

        # Remote notification on level 3
        if level == 3 and self.notif_cfg.enabled:
            _send_remote_alert(
                f"🚨 DrowsGuard ALERT: Driver drowsiness at critical level. {voice_msg}",
                self.notif_cfg,
            )

        # Update state
        self.state.active_level     = level
        self.state.issued_at        = now
        self.state.response_detected = False
        self.state.total_alerts    += 1
        if escalated:
            self.state.escalation_count += 1

        self.state.alert_history.append({
            "level":     level,
            "timestamp": now,
            "escalated": escalated,
            "label":     label,
        })

    def _cancel_alert(self):
        _stop_sound()
        self.state.active_level      = 0
        self.state.response_detected = True
        logger.info("Alert cancelled — driver is attentive.")
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
