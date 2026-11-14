# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
from fatigue import FatigueMonitor


def feed(monitor, strengths, gaps):
    """Record gestures with the given strengths and gaps between them."""
    now = 0.0
    for strength, gap in zip(strengths, gaps):
        now += gap
        monitor.record(strength, now)


def test_steady_user_is_not_tired():
    m = FatigueMonitor()
    feed(m, [0.8] * 10, [4.0] * 10)
    assert not m.is_tired()


def test_strength_drop_of_30_percent_is_tired():
    m = FatigueMonitor()
    feed(m, [0.8] * 5 + [0.56] * 5, [4.0] * 10)
    assert m.is_tired()


def test_small_strength_drop_is_not_tired():
    m = FatigueMonitor()
    feed(m, [0.8] * 5 + [0.7] * 5, [4.0] * 10)    # only 12.5%
    assert not m.is_tired()


def test_gaps_60_percent_longer_is_tired():
    m = FatigueMonitor()
    feed(m, [0.8] * 10, [4.0] * 5 + [6.4] * 5)
    assert m.is_tired()


def test_fewer_than_10_gestures_is_not_tired():
    m = FatigueMonitor()
    feed(m, [0.8] * 4 + [0.1] * 5, [4.0] * 4 + [20.0] * 5)
    assert not m.is_tired()


def test_reset_clears_history():
    m = FatigueMonitor()
    feed(m, [0.8] * 5 + [0.4] * 5, [4.0] * 10)
    assert m.is_tired()
    m.reset()
    assert m.strengths == [] and m.times == []
    assert not m.is_tired()
