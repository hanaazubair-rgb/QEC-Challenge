# SignalSpeak main program: calibrate two gestures, then let the user pick
# a need from a scanning board and have it spoken aloud.
#   eyebrows (hold) = select    mouth open (short hold) = undo
#   mouth open held 2 s = emergency "I need help now" (undo clears it)
# After the demo starts, no mouse/keyboard/voice input is used.
# Own design; generated with help from Claude (Anthropic) - see AI_USAGE.md.
import time

import cv2

import speech
from board import Board
from calibration import calibrate
from emergency import ALERT, UNDO, EmergencyAlert, JawGestures
from gestures import GestureDetector
from scanner import Scanner
from tracker import Tracker

OPTIONS = ["Yes", "No", "Water", "Pain", "Bathroom", "Call caregiver"]
SELECT_SIGNAL = "browInnerUp"
UNDO_SIGNAL = "jawOpen"


def calibrate_with_retry(tracker, signal, label, attempts=3):
    """Try calibration a few times; returns (baseline, peak) or None."""
    for _ in range(attempts):
        result = calibrate(tracker, signal, label)
        if result is not None:
            return result
        print(f"Calibration for {signal} was too weak, trying again.")
    return None


def handle_jaw(event, alert, scanner, message):
    """Act on a jaw event; returns the new board message."""
    if event == ALERT:
        phrase = alert.trigger()
        if phrase:
            speech.speak(phrase)
        return "Help is on the way. Open mouth briefly to cancel."
    if event == UNDO:
        if alert.active:
            alert.clear()
            return "Alert cancelled"
        cancelled = scanner.undo()
        return f"Cancelled: {cancelled}" if cancelled else ""
    return message


def main():
    tracker = Tracker()
    select_range = calibrate_with_retry(tracker, SELECT_SIGNAL,
                                        "raise your eyebrows")
    undo_range = calibrate_with_retry(tracker, UNDO_SIGNAL, "open your mouth")
    cv2.destroyAllWindows()
    if select_range is None or undo_range is None:
        print("Calibration failed. Check lighting and try again.")
        tracker.close()
        return

    select_gesture = GestureDetector(SELECT_SIGNAL, *select_range)
    jaw = JawGestures(*undo_range, signal=UNDO_SIGNAL)   # undo + alert
    alert = EmergencyAlert()
    scanner = Scanner(OPTIONS)
    # Start the voice BEFORE pygame opens, so pygame's audio setup
    # doesn't take over the sound device first.
    speech.speak("SignalSpeak ready")
    time.sleep(2)
    board = Board()
    message = "Raise your eyebrows to select"

    while board.handle_events():
        _, scores = tracker.read()
        now = time.time()
        if not alert.active:              # scanning pauses during an alert
            scanner.update(now)
        if scores:
            message = handle_jaw(jaw.update(scores[UNDO_SIGNAL], now),
                                 alert, scanner, message)
            if (select_gesture.update(scores[SELECT_SIGNAL], now)
                    and not alert.active and not scanner.is_paused()):
                message = scanner.select()
                speech.speak(message)
        board.draw(OPTIONS, scanner.index, message,
                   select_gesture.progress(now), alert.banner())

    tracker.close()


if __name__ == "__main__":
    main()