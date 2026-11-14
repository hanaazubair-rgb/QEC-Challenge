# SignalSpeak main program: calibrate two gestures (or load a saved
# profile), then let the user pick a need from a scanning board (with
# confirm step and pain scale) and have it spoken aloud. Adapts when the
# user tires (fatigue.py).
#   eyebrows (hold) = select    mouth open (hold) = undo / cancel
# Run: python main.py [--user NAME] [--recalibrate]
# After the demo starts, no mouse/keyboard/voice input is used.
# Own design; generated with help from Claude (Anthropic) - see AI_USAGE.md.
import argparse
import time

import cv2

import speech
from board import Board
from calibration import calibrate
from fatigue import FatigueMonitor
from flow import CONFIRM, MAIN_OPTIONS, Flow
from gestures import GestureDetector
from scanner import Scanner
from tracker import Tracker
from user_profile import load_profile, save_profile

SELECT_SIGNAL = "browInnerUp"
UNDO_SIGNAL = "jawOpen"
NOTICE_S = 3.0

# Full sentences for the short main-board labels (pain already is one).
PHRASES = {
    "Yes": "Yes.",
    "No": "No.",
    "Water": "I would like some water, please.",
    "Bathroom": "I need to use the bathroom.",
    "Call caregiver": "Please come here. I need my caregiver.",
}


def parse_args():
    parser = argparse.ArgumentParser(description="SignalSpeak")
    parser.add_argument("--user", default="default",
                        help="whose saved profile to use")
    parser.add_argument("--recalibrate", action="store_true",
                        help="ignore the saved profile and calibrate again")
    return parser.parse_args()


def calibrate_with_retry(tracker, signal, label, attempts=3):
    """Try calibration a few times; returns (baseline, peak) or None."""
    for _ in range(attempts):
        result = calibrate(tracker, signal, label)
        if result is not None:
            return result
        print(f"Calibration for {signal} was too weak, trying again.")
    return None


def get_profile(tracker, user, recalibrate):
    """Saved profile if there is one, else calibrate and save a new one."""
    profile = None if recalibrate else load_profile(user)
    if profile:
        print(f"Loaded saved profile '{user}'.")
        return profile
    select_range = calibrate_with_retry(tracker, SELECT_SIGNAL,
                                        "raise your eyebrows")
    undo_range = calibrate_with_retry(tracker, UNDO_SIGNAL, "open your mouth")
    cv2.destroyAllWindows()
    if select_range is None or undo_range is None:
        return None
    profile = {"select": list(select_range), "undo": list(undo_range)}
    save_profile(user, profile)
    print(f"Saved profile '{user}'.")
    return profile


def handle_undo(flow):
    """Undo: Cancel on the confirm screen, otherwise step back one option."""
    if flow.state == CONFIRM:
        flow.scanner.index = flow.options.index("Cancel")
        flow.select()
    else:
        flow.scanner.undo()


def main():
    args = parse_args()
    tracker = Tracker()
    profile = get_profile(tracker, args.user, args.recalibrate)
    if profile is None:
        print("Calibration failed. Check lighting and try again.")
        tracker.close()
        return

    select_gesture = GestureDetector(SELECT_SIGNAL, *profile["select"])
    undo_gesture = GestureDetector(UNDO_SIGNAL, *profile["undo"], hold_s=0.6)
    scanner = Scanner(MAIN_OPTIONS)
    saved_step = profile.get("step_s")
    if isinstance(saved_step, (int, float)) and saved_step > 0:
        scanner.step_s = float(saved_step)    # remember how slow they needed
    flow = Flow(scanner)
    monitor = FatigueMonitor()
    notice, notice_until = "", 0.0

    # Start the voice BEFORE pygame opens, so pygame's audio setup
    # doesn't take over the sound device first.
    speech.speak("SignalSpeak ready")
    time.sleep(2)
    board = Board()

    while board.handle_events():
        _, scores = tracker.read()
        now = time.time()
        scanner.update(now)
        if scores:
            if (select_gesture.update(scores[SELECT_SIGNAL], now)
                    and not scanner.is_paused()):
                monitor.record(select_gesture.last_strength, now)
                spoken = flow.select()
                if spoken:
                    speech.speak(PHRASES.get(spoken, spoken))
                if monitor.is_tired():
                    scanner.slow_down()
                    select_gesture.ease()
                    monitor.reset()
                    notice = "Getting tired? Slowing down to help."
                    notice_until = now + NOTICE_S
            if undo_gesture.update(scores[UNDO_SIGNAL], now):
                handle_undo(flow)
        shown = notice if now < notice_until else flow.message
        board.draw(flow.options, scanner.index, shown)

    profile["step_s"] = scanner.step_s
    save_profile(args.user, profile)
    tracker.close()


if __name__ == "__main__":
    main()