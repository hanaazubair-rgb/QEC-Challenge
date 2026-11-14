# Gesture detection for SignalSpeak: turns a noisy 0..1 signal into a
# deliberate "fired" event using a personal baseline/peak, hysteresis and a
# hold time. Own design; generated with help from Claude (Anthropic) -
# see AI_USAGE.md.

class GestureDetector:
    def __init__(self, signal, baseline, peak, hold_s=0.4,
                 on_frac=0.6, off_frac=0.35):
        self.signal = signal          # blendshape name, e.g. "browInnerUp"
        self.hold_s = hold_s
        self.on_frac = on_frac
        self.off_frac = off_frac
        self.set_range(baseline, peak)
        self.active = False
        self.fired = False
        self.start = 0.0

    def set_range(self, baseline, peak):
        """Recalibrate from the user's own resting and peak values."""
        span = max(peak - baseline, 1e-6)
        self.on_level = baseline + self.on_frac * span
        self.off_level = baseline + self.off_frac * span

    def update(self, value, now):
        """Feed one reading. Returns True once when held long enough."""
        if not self.active:
            if value >= self.on_level:
                self.active = True
                self.fired = False
                self.start = now
            return False
        if value <= self.off_level:   # released
            self.active = False
            return False
        if not self.fired and now - self.start >= self.hold_s:
            self.fired = True
            return True
        return False