# SignalSpeak demo: calibrate, then hold the gesture to "select".
# Own design; generated with help from Claude (Anthropic) - see AI_USAGE.md.
import time

import cv2

from calibration import calibrate
from gestures import GestureDetector
from tracker import Tracker

SIGNAL = "browInnerUp"


def main():
    tracker = Tracker()
    result = calibrate(tracker, SIGNAL, "raise your eyebrows")
    if result is None:
        print("Calibration failed: gesture too weak. Try again.")
        return
    baseline, peak = result
    detector = GestureDetector(SIGNAL, baseline, peak)
    selections = 0
    flash_until = 0.0
    while True:
        frame, scores = tracker.read()
        if frame is None:
            break
        now = time.time()
        if scores and detector.update(scores[SIGNAL], now):
            selections += 1
            flash_until = now + 0.5
        color = (0, 255, 0) if now < flash_until else (255, 255, 255)
        cv2.putText(frame, f"Selections: {selections}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow("SignalSpeak", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):   # dev-only quit key
            break
    tracker.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()