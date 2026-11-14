# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
from flow import CONFIRM, MAIN, PAIN, Flow
from scanner import Scanner


def make() -> Flow:
    return Flow(Scanner(["placeholder"], step_s=1.0, pause_s=0.0))


def pick(flow: Flow, option: str) -> str | None:
    """Move the highlight to option, then select it."""
    flow.scanner.index = flow.options.index(option)
    return flow.select()


def test_starts_on_main_board():
    f = make()
    assert f.state == MAIN
    assert "Water" in f.options


def test_select_asks_for_confirmation_without_speaking():
    f = make()
    assert pick(f, "Water") is None
    assert f.state == CONFIRM
    assert f.message == "Send WATER?"
    assert f.options == ["Confirm", "Cancel"]


def test_confirm_speaks_and_returns_to_main():
    f = make()
    pick(f, "Water")
    assert pick(f, "Confirm") == "Water"
    assert f.state == MAIN
    assert f.message == "Water"


def test_cancel_speaks_nothing():
    f = make()
    pick(f, "Bathroom")
    assert pick(f, "Cancel") is None
    assert f.state == MAIN
    assert f.message == "Cancelled"


def test_pain_opens_scale():
    f = make()
    assert pick(f, "Pain") is None
    assert f.state == PAIN
    assert f.options[:10] == [str(n) for n in range(1, 11)]


def test_pain_level_is_confirmed_then_spoken():
    f = make()
    pick(f, "Pain")
    assert pick(f, "7") is None
    assert f.message == "Send PAIN 7/10?"
    assert pick(f, "Confirm") == "My pain is 7 out of 10"


def test_pain_back_returns_to_main():
    f = make()
    pick(f, "Pain")
    pick(f, "Back")
    assert f.state == MAIN


def test_new_screen_starts_scanning_from_first_option():
    f = make()
    f.scanner.update(0.0)
    pick(f, "Call caregiver")
    assert f.scanner.update(0.5) == 0
