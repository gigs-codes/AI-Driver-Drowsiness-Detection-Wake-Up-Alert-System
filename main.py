"""
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

import cv2

import config as cfg
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

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.release()
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
