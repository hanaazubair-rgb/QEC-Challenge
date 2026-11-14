from gestures import GestureDetector


def make():
    return GestureDetector("browInnerUp", baseline=0.2, peak=0.8, hold_s=0.4)


def test_brief_spike_does_not_fire():
    g = make()
    assert not g.update(0.8, 0.0)
    assert not g.update(0.8, 0.2)
    assert not g.update(0.2, 0.3)   # released before hold time


def test_held_gesture_fires_once():
    g = make()
    g.update(0.8, 0.0)
    assert g.update(0.8, 0.5)
    assert not g.update(0.8, 0.9)   # no repeat while still held


def test_fires_again_after_release():
    g = make()
    g.update(0.8, 0.0)
    assert g.update(0.8, 0.5)
    g.update(0.2, 0.6)              # release
    g.update(0.8, 1.0)
    assert g.update(0.8, 1.5)


def test_recalibration_changes_threshold():
    g = make()
    g.set_range(0.0, 1.0)           # 0.5 is now below the on level (0.6)
    g.update(0.5, 0.0)
    assert not g.update(0.5, 1.0)
