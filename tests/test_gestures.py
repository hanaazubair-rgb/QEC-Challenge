import pytest

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
    g.update(0.2, 0.6)              # goes low
    g.update(0.2, 0.9)              # stays low 0.3 s -> released
    g.update(0.8, 1.0)
    assert g.update(0.8, 1.5)


def test_brief_dip_does_not_retrigger():
    g = make()
    g.update(0.8, 0.0)
    assert g.update(0.8, 0.5)
    g.update(0.2, 0.6)              # flicker low for 0.1 s
    g.update(0.8, 0.7)              # back up: still the same hold
    assert not g.update(0.8, 1.2)   # must not fire a second time


def test_recalibration_changes_threshold():
    g = make()
    g.set_range(0.0, 1.0)           # 0.5 is now below the on level (0.6)
    g.update(0.5, 0.0)
    assert not g.update(0.5, 1.0)


def test_held_0_3s_does_not_fire():
    g = make()
    g.update(0.8, 0.0)
    assert not g.update(0.8, 0.3)


def test_held_0_5s_fires_exactly_once():
    g = make()
    fired = [g.update(0.8, t / 10) for t in range(0, 11)]   # 0.0 .. 1.0 s
    assert fired.count(True) == 1
    assert fired.index(True) == 4                            # at 0.4 s


def test_does_not_fire_again_until_released():
    g = make()
    g.update(0.8, 0.0)
    assert g.update(0.8, 0.5)
    assert not any(g.update(0.8, 0.5 + t / 10) for t in range(1, 20))
    g.update(0.2, 2.6)
    g.update(0.2, 2.9)              # released
    g.update(0.8, 3.0)
    assert g.update(0.8, 3.5)


def test_last_strength_is_strongest_value():
    g = make()
    g.update(0.7, 0.0)
    g.update(0.9, 0.2)
    g.update(0.75, 0.3)
    assert g.update(0.72, 0.5)
    assert g.last_strength == 0.9


def test_last_strength_resets_each_gesture():
    g = make()
    g.update(0.95, 0.0)
    g.update(0.95, 0.5)
    g.update(0.2, 0.6)
    g.update(0.2, 0.9)              # released
    g.update(0.7, 1.0)
    assert g.update(0.7, 1.5)
    assert g.last_strength == 0.7


def test_ease_lowers_threshold():
    g = make()
    before = g.on_level
    g.ease()
    assert g.on_level < before
    assert abs(g.on_frac - 0.6 * 0.85) < 1e-9


def test_ease_has_minimum_and_keeps_hysteresis():
    g = make()
    for _ in range(20):
        g.ease()
    assert g.on_frac == 0.3
    assert g.off_level < g.on_level


def test_bad_calibration_raises():
    with pytest.raises(ValueError, match="no movement"):
        GestureDetector("browInnerUp", baseline=0.5, peak=0.5)
    g = make()
    with pytest.raises(ValueError):
        g.set_range(0.6, 0.4)


def test_progress_is_zero_when_not_holding():
    g = make()
    assert g.progress(0.0) == 0.0
    g.update(0.2, 0.0)              # below the on level
    assert g.progress(0.1) == 0.0


def test_progress_fills_during_hold():
    g = make()                      # hold_s = 0.4
    g.update(0.8, 1.0)
    assert g.progress(1.0) == 0.0
    assert abs(g.progress(1.2) - 0.5) < 1e-9
    assert g.progress(5.0) == 1.0   # capped at full


def test_progress_resets_after_firing():
    g = make()
    g.update(0.8, 0.0)
    assert g.update(0.8, 0.5)
    assert g.progress(0.6) == 0.0
