# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Scanner for SignalSpeak: highlights one option at a time and moves on by
# itself, so the user only needs ONE gesture ("select"). Pure Python, no
# pygame, so it can be tested with fake times.


class Scanner:
    """Step a highlight through a list of options on a timer."""

    def __init__(self, options: list[str], step_s: float = 1.5,
                 pause_s: float = 2.0, slow_step_s: float = 0.5,
                 max_step_s: float = 5.0) -> None:
        if not options:
            raise ValueError("Scanner needs at least one option")
        self.options = list(options)
        self.step_s = step_s
        self.pause_s = pause_s            # freeze after a selection
        self.slow_step_s = slow_step_s    # how much slow_down() adds
        self.max_step_s = max_step_s
        self.index = 0
        self.last_selection: str | None = None
        self._now = 0.0                   # latest time seen by update()
        self._last_step: float | None = None
        self._paused_until = 0.0

    def update(self, now: float) -> int:
        """Advance the highlight based on time. Returns the current index."""
        self._now = now
        if self._last_step is None:
            self._last_step = now
        if self.is_paused():
            self._last_step = now         # restart the step timer after pause
            return self.index
        steps = int((now - self._last_step) // self.step_s)
        if steps > 0:
            self.index = (self.index + steps) % len(self.options)
            self._last_step += steps * self.step_s
        return self.index

    def is_paused(self) -> bool:
        """True while scanning is frozen after a selection."""
        return self._now < self._paused_until

    def select(self) -> str:
        """Choose the highlighted option and pause scanning briefly."""
        self.last_selection = self.options[self.index]
        self._paused_until = self._now + self.pause_s
        return self.last_selection

    def undo(self) -> str | None:
        """Cancel the last selection, or step back one option if none.

        Returns the cancelled option, or None if we only moved back.
        """
        self._last_step = self._now       # give the user a full step
        if self.last_selection is not None:
            cancelled = self.last_selection
            self.last_selection = None
            self._paused_until = 0.0      # resume scanning now
            return cancelled
        self.index = (self.index - 1) % len(self.options)
        return None

    def slow_down(self) -> float:
        """Make scanning slower (for when the user tires). Returns step_s."""
        self.step_s = min(self.step_s + self.slow_step_s, self.max_step_s)
        return self.step_s
