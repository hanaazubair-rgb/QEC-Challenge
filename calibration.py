# Per-user calibration for SignalSpeak. Own design; generated with help from
# Claude (Anthropic) - see AI_USAGE.md. Uses OpenCV [cv2] for on-screen prompts.
import statistics
import time

import cv2

MIN_SPAN = 0.15   # smaller gap than this = gesture too weak to trust


def compute_range(rest_values, peak_values, min_span=MIN_SPAN):
    """Returns (baseline, peak) from samples, or None if too weak/short."""
    if len(rest_values) < 5 or len(peak_values) < 5:
        return None
    baseline = statistics.median(rest_values)
    peak = statistics.quantiles(peak_values, n=10)[-1]   # 90th percentile
    if peak - baseline < min_span:
        return None
    return baseline, peak


def _collect(tracker, signal, seconds, message):
    values = []
    end = time.time() + seconds
    while time.time() < end:
        frame, scores = tracker.read()
        if frame is None:
            break
        if scores and signal in scores:
            values.append(scores[signal])
        cv2.putText(frame, message, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
        cv2.imshow("SignalSpeak", frame)
        cv2.waitKey(1)
    return values


def calibrate(tracker, signal, label, seconds=3):
    """Guides the user with on-screen text only (no keyboard needed)."""
    rest = _collect(tracker, signal, seconds, "Relax your face")
    peak = _collect(tracker, signal, seconds, f"Now: {label} and hold")
    return compute_range(rest, peak)