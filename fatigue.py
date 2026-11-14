# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Fatigue monitor for SignalSpeak (personalization). People with ALS tire
# during a session: gestures get weaker and come further apart. This
# notices that so the app can slow scanning and ease the gesture threshold.
# Pure Python, no pygame/cv2, so it is unit-testable.

from statistics import mean

WINDOW = 5               # gestures compared at the start vs. most recently
STRENGTH_DROP = 0.25     # last 5 are 25%+ weaker than the first 5 = tired
GAP_GROWTH = 0.50        # last 5 are 50%+ further apart than the first 5
MIN_GESTURES = 2 * WINDOW


class FatigueMonitor:
    """Compare the user's first gestures with their most recent ones."""

    def __init__(self) -> None:
        self.strengths: list[float] = []
        self.times: list[float] = []

    def record(self, strength: float, now: float) -> None:
        """Store one gesture's strength (0-1) and when it happened."""
        self.strengths.append(strength)
        self.times.append(now)

    def is_tired(self) -> bool:
        """True if gestures got much weaker or much further apart."""
        if len(self.strengths) < MIN_GESTURES:
            return False
        return self._weaker() or self._slower()

    def reset(self) -> None:
        """Clear history, e.g. right after the app has adapted."""
        self.strengths.clear()
        self.times.clear()

    def _weaker(self) -> bool:
        first = mean(self.strengths[:WINDOW])
        last = mean(self.strengths[-WINDOW:])
        return last <= (1 - STRENGTH_DROP) * first

    def _slower(self) -> bool:
        first = _mean_gap(self.times[:WINDOW])
        last = _mean_gap(self.times[-WINDOW:])
        return last >= (1 + GAP_GROWTH) * first


def _mean_gap(times: list[float]) -> float:
    """Average time between consecutive gestures."""
    return mean(b - a for a, b in zip(times, times[1:]))
