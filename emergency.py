# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Emergency alert for SignalSpeak. The mouth-open (jawOpen) gesture does two
# jobs, told apart by how long it is held:
#   short hold (0.6 s, then release)  -> undo
#   long hold  (2 s)                  -> emergency alert, fires immediately
# Undo waits for the release, so a long hold never also triggers an undo.
# Pure Python, no pygame/cv2, so it is unit-testable.

from gestures import GestureDetector

ALERT_HOLD_S = 2.0
UNDO_HOLD_S = 0.6
HELP_PHRASE = "I need help now. I need help now."   # one call = said twice
BANNER = "HELP REQUESTED"

UNDO, ALERT = "undo", "alert"


class JawGestures:
    """Turns one calibrated jawOpen signal into 'undo' or 'alert' events."""

    def __init__(self, baseline: float, peak: float,
                 signal: str = "jawOpen") -> None:
        self.undo = GestureDetector(signal, baseline, peak,
                                    hold_s=UNDO_HOLD_S)
        self.alert = GestureDetector(signal, baseline, peak,
                                     hold_s=ALERT_HOLD_S)
        self._undo_pending = False

    def update(self, value: float, now: float) -> str | None:
        """Feed one reading. Returns UNDO, ALERT or None."""
        alert_fired = self.alert.update(value, now)
        undo_held = self.undo.update(value, now)
        if alert_fired:
            self._undo_pending = False    # it was a long hold, not an undo
            return ALERT
        if undo_held:
            self._undo_pending = True     # decide once the mouth closes
        if self._undo_pending and not self.undo.active:
            self._undo_pending = False
            return UNDO
        return None


class EmergencyAlert:
    """Whether a help request is showing. Cleared only by the undo gesture."""

    def __init__(self) -> None:
        self.active = False

    def trigger(self) -> str | None:
        """Start the alert. Returns the phrase to speak (once per alert)."""
        if self.active:
            return None
        self.active = True
        return HELP_PHRASE

    def clear(self) -> None:
        self.active = False

    def banner(self) -> str | None:
        """Text for the board's red banner, or None when no alert."""
        return BANNER if self.active else None
