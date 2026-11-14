# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
from fatigue import FatigueMonitor
from gestures import GestureDetector
from scanner import Scanner


def make():
    scanner = Scanner(["Yes", "No"], step_s=1.5)
    detector = GestureDetector("browInnerUp", baseline=0.0, peak=1.0)
    return FatigueMonitor(scanner, detector), scanner, detector


def feed(monitor, strengths, times):
    return [monitor.record(s, t) for s, t in zip(strengths, times)]


def test_needs_ten_gestures_before_judging():
    m, scanner, _ = make()
    assert feed(m, [0.9] * 4 + [0.1] * 5, [2.0] * 9) == [False] * 9
    assert scanner.step_s == 1.5


def test_steady_user_is_not_fatigued():
    m, scanner, detector = make()
    assert not any(feed(m, [0.9] * 10, [2.0] * 10))
    assert scanner.step_s == 1.5
    assert detector.on_level == 0.6


def test_small_drop_is_ignored():
    m, _, _ = make()
    assert not any(feed(m, [0.8] * 5 + [0.7] * 5, [2.0] * 10))  # 12.5%


def test_weaker_gestures_trigger_adaptation():
    m, scanner, detector = make()
    results = feed(m, [0.8] * 5 + [0.6] * 5, [2.0] * 10)    # exactly 25%
    assert results[-1] is True
    assert scanner.step_s == 2.0
    assert detector.on_level < 0.6
    assert detector.on_level > detector.off_level


def test_slower_selections_trigger_adaptation():
    m, scanner, _ = make()
    assert feed(m, [0.8] * 10, [2.0] * 5 + [2.5] * 5)[-1] is True
    assert scanner.step_s == 2.0


def test_does_not_retrigger_without_further_decline():
    m, scanner, _ = make()
    feed(m, [0.8] * 5 + [0.6] * 5, [2.0] * 10)
    assert not any(feed(m, [0.6] * 10, [2.0] * 10))
    assert m.adaptations == 1
    assert scanner.step_s == 2.0


def test_further_decline_adapts_again():
    m, scanner, _ = make()
    feed(m, [0.8] * 5 + [0.6] * 5, [2.0] * 10)
    feed(m, [0.4] * 5, [2.0] * 5)                           # 0.6 -> 0.4
    assert m.adaptations == 2
    assert scanner.step_s == 2.5
