"""
<<<<<<< HEAD
main.py
-------
DrowsGuard — AI Driver Drowsiness Detection System
Entry point.

Run:
    python main.py

Controls:
    q  → quit
    d  → toggle dashboard window
    r  → reset fatigue state
"""

import sys
import time
import logging
import argparse
=======
main.py — DrowsGuard entry point
AI Driver Drowsiness Detection + Wake-Up Alert System

Usage
-----
    python main.py                        # webcam, default settings
    python main.py --source video.mp4     # video file
    python main.py --mesh                 # show face mesh overlay
    python main.py --no-dashboard         # headless / embedded mode
    python main.py --notify               # enable Twilio/Telegram alerts
"""

import argparse
import logging
import os
import sys
import time
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3

import cv2

import config as cfg
<<<<<<< HEAD
from detector import Detector
from dashboard import Dashboard


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt = "%H:%M:%S",
)
log = logging.getLogger("drowsguard")


# ---------------------------------------------------------------------------
# CLI arguments
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="DrowsGuard — AI Driver Drowsiness Detection System"
    )
    p.add_argument(
        "--camera", type=int, default=cfg.CAMERA_INDEX,
        help="Webcam device index (default: 0)"
    )
    p.add_argument(
        "--no-dashboard", action="store_true",
        help="Disable the matplotlib dashboard window"
    )
    p.add_argument(
        "--width",  type=int, default=cfg.CAMERA_WIDTH,
        help="Capture width (default: 640)"
    )
    p.add_argument(
        "--height", type=int, default=cfg.CAMERA_HEIGHT,
        help="Capture height (default: 480)"
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> int:
    args = parse_args()

    # ── Open webcam ───────────────────────────────────────────────────────
    log.info("Opening camera %d …", args.camera)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        log.error("Cannot open camera %d. Try a different --camera index.", args.camera)
        return 1

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, cfg.TARGET_FPS)

    # ── Initialise components ─────────────────────────────────────────────
    detector  = Detector()
    dashboard = None if args.no_dashboard else Dashboard()

    log.info("DrowsGuard started. Press [q] to quit, [d] toggle dashboard, [r] reset state.")
    log.info("Monitoring driver …")

    # ── FPS tracking ──────────────────────────────────────────────────────
    fps        = 0.0
    frame_times: list = []
    t_prev = time.perf_counter()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                log.warning("Frame grab failed — skipping.")
                continue

            # ── Process frame ─────────────────────────────────────────────
            result = detector.process_frame(frame)

            # ── FPS calculation ───────────────────────────────────────────
            t_now = time.perf_counter()
            frame_times.append(t_now - t_prev)
            t_prev = t_now
            if len(frame_times) > 30:
                frame_times.pop(0)
            fps = 1.0 / (sum(frame_times) / len(frame_times))

            # ── FPS readout on frame ──────────────────────────────────────
            cv2.putText(
                frame, f"FPS: {fps:.1f}",
                (frame.shape[1] - 90, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1, cv2.LINE_AA,
            )

            # ── Show video window ─────────────────────────────────────────
            cv2.imshow("DrowsGuard", frame)

            # ── Update dashboard ──────────────────────────────────────────
            if dashboard:
                dashboard.update(result, fps)

            # ── Keyboard controls ─────────────────────────────────────────
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                log.info("Quit requested.")
                break

            elif key == ord("d"):
                if dashboard is None:
                    log.info("Opening dashboard.")
                    dashboard = Dashboard()
                else:
                    log.info("Closing dashboard.")
                    dashboard.close()
                    dashboard = None

            elif key == ord("r"):
                log.info("Fatigue state reset.")
                detector.state.__init__()          # reset counters

    except KeyboardInterrupt:
        log.info("Interrupted.")

=======
from detector   import DrowsinessDetector
from alerter    import DrowsinessAlerter
from dashboard  import SessionLogger, LiveDashboard

# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────
os.makedirs(cfg.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(cfg.LOG_DIR, "drowsguard.log")),
    ],
)
logger = logging.getLogger("drowsguard.main")


# ─────────────────────────────────────────────
#  CLI args
# ─────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="DrowsGuard — AI Driver Drowsiness Detection",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--source",        default=str(cfg.CAMERA_INDEX),
                   help="Camera index or path to video file")
    p.add_argument("--width",         type=int,   default=cfg.FRAME_WIDTH)
    p.add_argument("--height",        type=int,   default=cfg.FRAME_HEIGHT)
    p.add_argument("--mesh",          action="store_true",
                   help="Overlay MediaPipe face mesh tessellation")
    p.add_argument("--no-dashboard",  action="store_true",
                   help="Disable live matplotlib dashboard")
    p.add_argument("--notify",        action="store_true",
                   help="Enable Twilio/Telegram remote notifications")
    p.add_argument("--ear-thresh",    type=float, default=cfg.EAR_THRESHOLD,
                   help="Eye Aspect Ratio closed threshold")
    p.add_argument("--risk1",         type=float, default=cfg.RISK_LEVEL1)
    p.add_argument("--risk2",         type=float, default=cfg.RISK_LEVEL2)
    p.add_argument("--risk3",         type=float, default=cfg.RISK_LEVEL3)
    return p.parse_args()


# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────
def run(args: argparse.Namespace) -> None:
    # ── Apply CLI overrides to config
    cfg.EAR_THRESHOLD = args.ear_thresh
    cfg.RISK_LEVEL1   = args.risk1
    cfg.RISK_LEVEL2   = args.risk2
    cfg.RISK_LEVEL3   = args.risk3

    # ── Build notification config
    notif_cfg = cfg.NotificationConfig(enabled=args.notify)
    if args.notify:
        notif_cfg.twilio_sid    = os.getenv("TWILIO_SID")
        notif_cfg.twilio_token  = os.getenv("TWILIO_TOKEN")
        notif_cfg.twilio_from   = os.getenv("TWILIO_FROM")
        notif_cfg.alert_phone   = os.getenv("ALERT_PHONE")
        notif_cfg.telegram_token    = os.getenv("TELEGRAM_TOKEN")
        notif_cfg.telegram_chat_id  = os.getenv("TELEGRAM_CHAT_ID")

    # ── Open video source
    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        logger.error("Could not open source: %s", source)
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    # ── Instantiate components
    detector  = DrowsinessDetector(draw_mesh=args.mesh)
    alerter   = DrowsinessAlerter(notif_cfg=notif_cfg)
    session   = SessionLogger()
    dashboard = LiveDashboard() if not args.no_dashboard else None

    logger.info("DrowsGuard started.  Press 'q' to quit, 'r' to reset session.")
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║   DrowsGuard — AI Drowsiness Monitor  ║")
    print("  ╚══════════════════════════════════════╝")
    print("  Press  q → quit  |  r → reset  |  m → toggle mesh\n")

    fps_counter = 0
    fps_start   = time.monotonic()
    fps_display = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                logger.info("End of video stream.")
                break

            # ── Detect
            result = detector.process(frame)

            # ── Alert
            attentive = detector.is_attentive(result)
            alert_state = alerter.check(result.alert_level, attentive)

            # ── Log
            session.log_frame(result)
            if dashboard:
                dashboard.push(result)

            # ── FPS
            fps_counter += 1
            elapsed = time.monotonic() - fps_start
            if elapsed >= 1.0:
                fps_display  = fps_counter / elapsed
                fps_counter  = 0
                fps_start    = time.monotonic()

            # ── Show
            display = result.annotated_frame if result.annotated_frame is not None else frame
            cv2.putText(display, f"FPS: {fps_display:.1f}", (display.shape[1] - 80, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)
            cv2.putText(display, f"Alerts: {alert_state.total_alerts}", (display.shape[1] - 100, 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1, cv2.LINE_AA)

            cv2.imshow("DrowsGuard", display)

            # ── Key handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("r"):
                alerter.reset()
                logger.info("Session reset by user.")
            elif key == ord("m"):
                detector.draw_mesh = not detector.draw_mesh

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.release()
<<<<<<< HEAD
        if dashboard:
            dashboard.close()
        log.info(
            "Session summary — yawns: %d  blink events: %d",
            detector.state.total_yawns,
            detector.state.total_blink_events,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
=======
        summary = session.close()
        session.print_summary(summary)


# ─────────────────────────────────────────────
if __name__ == "__main__":
    run(parse_args())
>>>>>>> 942b7caa1b8ce0ed4465081148a7de6d1c21f4b3
