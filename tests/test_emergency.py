# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
from emergency import (ALERT, BANNER, HELP_PHRASE, UNDO, EmergencyAlert,
                       JawGestures)

OPEN, CLOSED = 0.8, 0.1


def make() -> JawGestures:
    return JawGestures(baseline=0.0, peak=1.0)


def run(jaw, value, start, end, step=0.05):
    """Feed a constant value from start to end; return non-None events."""
    events, t = [], start
    while t <= end + 1e-9:
        event = jaw.update(value, t)
        if event:
            events.append((event, round(t, 2)))
        t += step
    return events


def test_short_hold_is_undo_after_release():
    jaw = make()
    assert run(jaw, OPEN, 0.0, 1.0) == []          # nothing while held
    events = run(jaw, CLOSED, 1.05, 1.6)
    assert [e for e, _ in events] == [UNDO]


def test_very_short_hold_does_nothing():
    jaw = make()
    run(jaw, OPEN, 0.0, 0.3)
    assert run(jaw, CLOSED, 0.35, 1.0) == []


def test_two_second_hold_is_alert_immediately():
    jaw = make()
    events = run(jaw, OPEN, 0.0, 2.5)
    assert events == [(ALERT, 2.0)]


def test_long_hold_does_not_also_undo():
    jaw = make()
    run(jaw, OPEN, 0.0, 3.0)
    assert run(jaw, CLOSED, 3.05, 4.0) == []


def test_undo_works_again_after_alert():
    jaw = make()
    run(jaw, OPEN, 0.0, 2.5)
    run(jaw, CLOSED, 2.55, 3.0)
    run(jaw, OPEN, 3.05, 4.0)
    events = run(jaw, CLOSED, 4.05, 4.6)
    assert [e for e, _ in events] == [UNDO]


def test_alert_speaks_once_and_shows_banner():
    alert = EmergencyAlert()
    assert alert.banner() is None
    assert alert.trigger() == HELP_PHRASE
    assert HELP_PHRASE.count("I need help now") == 2
    assert alert.trigger() is None                 # no repeat while active
    assert alert.banner() == BANNER


def test_clear_ends_alert():
    alert = EmergencyAlert()
    alert.trigger()
    alert.clear()
    assert not alert.active
    assert alert.trigger() == HELP_PHRASE          # can be raised again
