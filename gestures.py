# Gesture detection for SignalSpeak: turns a noisy 0..1 signal into a
# deliberate "fired" event using a personal baseline/peak, hysteresis, a
# hold time and a release delay. Own design; generated with help from
# Claude (Anthropic) - see AI_USAGE.md.


class GestureDetector:
    def __init__(self, signal, baseline, peak, hold_s=0.4,
                 on_frac=0.6, off_frac=0.35, release_s=0.2):
        self.signal = signal          # blendshape name, e.g. "browInnerUp"
        self.hold_s = hold_s
        self.release_s = release_s    # must stay low this long to release
        self.on_frac = on_frac
        self.off_frac = off_frac
        self.set_range(baseline, peak)
        self.active = False
        self.fired = False
        self.start = 0.0
        self.below_since = None
        self.max_value = 0.0          # strongest reading in this gesture
        self.last_strength = 0.0      # strength of the last fired gesture

    def set_range(self, baseline, peak):
        """Recalibrate from the user's own resting and peak values."""
        if peak <= baseline:
            raise ValueError("calibration failed - no movement detected")
        self.baseline = baseline
        self.peak = peak
        self._update_levels()

    def _update_levels(self):
        """Turn the fractions into absolute on/off thresholds."""
        span = self.peak - self.baseline
        self.on_level = self.baseline + self.on_frac * span
        self.off_level = self.baseline + self.off_frac * span

    def ease(self, factor=0.85, min_on_frac=0.3):
        """Lower the trigger level when the user is tiring.

        The release level is kept at least 0.1 below the trigger level so
        hysteresis still filters noise.
        """
        self.on_frac = max(self.on_frac * factor, min_on_frac)
        self.off_frac = min(self.off_frac, self.on_frac - 0.1)
        self._update_levels()

    def progress(self, now):
        """How far through the hold the user is: 0..1.

        0 when no gesture is being held or it has already fired, so a UI
        can draw a filling bar while the user holds the gesture.
        """
        if not self.active or self.fired:
            return 0.0
        return min(max((now - self.start) / self.hold_s, 0.0), 1.0)

    def update(self, value, now):
        """Feed one reading. Returns True once when held long enough."""
        if not self.active:
            if value >= self.on_level:
                self.active = True
                self.fired = False
                self.start = now
                self.below_since = None
                self.max_value = value
            return False
        if value <= self.off_level:   # low: released only if it stays low
            if self.below_since is None:
                self.below_since = now
            if now - self.below_since >= self.release_s:
                self.active = False
            return False
        self.below_since = None       # back up: the dip was just flicker
        self.max_value = max(self.max_value, value)
        if not self.fired and now - self.start >= self.hold_s:
            self.fired = True
            self.last_strength = self.max_value
            return True
        return False