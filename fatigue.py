# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Fatigue monitor for SignalSpeak (personalization). People with ALS tire
# during a session: gestures get weaker and selecting takes longer. This
# notices that and makes the app easier to use: slower scanning and a lower
# gesture threshold. Pure Python, no pygame/cv2, so it is unit-testable.

from statistics import mean
from typing import Protocol

WINDOW = 5               # gestures per average
STRENGTH_DROP = 0.25     # 25% weaker than the start = tired
SLOWER_BY = 0.25         # 25% slower than the start = tired


class SlowableScanner(Protocol):
    def slow_down(self) -> float: ...


class Easable(Protocol):
    def ease(self, factor: float = 0.85) -> None: ...


class FatigueMonitor:
    """Watch gesture strength and selection time; adapt when the user tires."""

    def __init__(self, scanner: SlowableScanner, detector: Easable) -> None:
        self.scanner = scanner
        self.detector = detector
        self.strengths: list[float] = []
        self.times: list[float] = []
        self.adaptations = 0

    def record(self, strength: float, select_time_s: float) -> bool:
        """Log one selection. Returns True if the app was adapted."""
        self.strengths.append(strength)
        self.times.append(select_time_s)
        if not self.is_fatigued():
            return False
        self._adapt()
        return True

    def is_fatigued(self) -> bool:
        """Compare the last 5 gestures with the first 5 of this period."""
        if len(self.strengths) < 2 * WINDOW:
            return False
        weaker = self._recent(self.strengths) <= (
            (1 - STRENGTH_DROP) * self._start(self.strengths))
        slower = self._recent(self.times) >= (
            (1 + SLOWER_BY) * self._start(self.times))
        return weaker or slower

    def _adapt(self) -> None:
        """Slow scanning, lower the threshold, and start a fresh baseline."""
        self.scanner.slow_down()
        self.detector.ease()          # weaker gestures now count
        self.adaptations += 1
        # The tired level becomes the new "start", so we only react again
        # if the user gets even more tired.
        self.strengths = self.strengths[-WINDOW:]
        self.times = self.times[-WINDOW:]

    @staticmethod
    def _start(values: list[float]) -> float:
        return mean(values[:WINDOW])

    @staticmethod
    def _recent(values: list[float]) -> float:
        return mean(values[-WINDOW:])
