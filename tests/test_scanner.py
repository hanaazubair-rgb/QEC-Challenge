# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
import pytest

from scanner import Scanner

OPTIONS = ["Yes", "No", "Water", "Pain", "Bathroom", "Call caregiver"]


def make() -> Scanner:
    s = Scanner(OPTIONS, step_s=1.5, pause_s=2.0)
    s.update(0.0)
    return s


def test_starts_on_first_option():
    assert make().update(0.0) == 0


def test_advances_one_step_per_interval():
    s = make()
    assert s.update(1.4) == 0
    assert s.update(1.5) == 1
    assert s.update(3.0) == 2


def test_wraps_around():
    s = make()
    assert s.update(1.5 * 6) == 0
    assert s.update(1.5 * 7) == 1


def test_select_returns_highlighted_option():
    s = make()
    s.update(3.0)
    assert s.select() == "Water"


def test_select_pauses_scanning():
    s = make()
    s.update(3.0)
    s.select()
    assert s.is_paused()
    assert s.update(4.9) == 2          # frozen during the pause
    assert s.update(5.0) == 2          # pause ends, timer restarts
    assert s.update(6.5) == 3


def test_undo_after_select_cancels_and_resumes():
    s = make()
    s.update(1.5)
    s.select()
    assert s.undo() == "No"
    assert s.last_selection is None
    assert not s.is_paused()
    assert s.update(3.0) == 2


def test_undo_without_selection_moves_back_one():
    s = make()
    s.update(3.0)
    assert s.undo() is None
    assert s.index == 1


def test_undo_from_first_wraps_to_last():
    s = make()
    s.undo()
    assert s.index == len(OPTIONS) - 1


def test_second_undo_moves_back():
    s = make()
    s.update(3.0)
    s.select()
    s.undo()                            # cancels selection
    s.undo()                            # then moves back
    assert s.index == 1


def test_slow_down_increases_step_and_caps():
    s = Scanner(OPTIONS, step_s=1.5, slow_step_s=0.5, max_step_s=2.5)
    assert s.slow_down() == 2.0
    assert s.slow_down() == 2.5
    assert s.slow_down() == 2.5


def test_slow_down_changes_timing():
    s = make()
    s.slow_down()                       # now 2.0 s per step
    assert s.update(1.5) == 0
    assert s.update(2.0) == 1


def test_set_options_switches_screen_and_resets():
    s = make()
    s.update(3.0)
    s.select()
    s.set_options(["Confirm", "Cancel"])
    assert s.options == ["Confirm", "Cancel"]
    assert s.index == 0
    assert s.last_selection is None


def test_empty_options_rejected():
    with pytest.raises(ValueError):
        Scanner([])
