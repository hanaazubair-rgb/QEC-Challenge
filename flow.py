# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Conversation flow for SignalSpeak: which screen we are on and what a
# selection means. Every message is confirmed before it is spoken, so an
# accidental gesture never says the wrong thing out loud. Pain opens a 1-10
# sub-menu. Pure Python, no pygame, so it is unit-testable.

from scanner import Scanner

MAIN_OPTIONS = ["Yes", "No", "Water", "Pain", "Bathroom", "Call caregiver"]
PAIN_OPTIONS = [str(n) for n in range(1, 11)] + ["Back"]
CONFIRM_OPTIONS = ["Confirm", "Cancel"]

MAIN, PAIN, CONFIRM = "main", "pain", "confirm"


class Flow:
    """Moves between the main board, the pain scale and the confirm screen."""

    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner
        self.state = MAIN
        self.message = "Choose a message"
        self._pending_label = ""
        self._pending_phrase = ""
        self.scanner.set_options(MAIN_OPTIONS)

    @property
    def options(self) -> list[str]:
        """Options on the current screen."""
        return self.scanner.options

    def select(self) -> str | None:
        """Select the highlighted option. Returns text to speak, or None."""
        choice = self.scanner.select()
        if self.state == MAIN:
            self._choose_main(choice)
        elif self.state == PAIN:
            self._choose_pain(choice)
        else:
            return self._choose_confirm(choice)
        return None

    def _choose_main(self, choice: str) -> None:
        if choice == "Pain":
            self._go(PAIN, PAIN_OPTIONS, "How bad is the pain?")
        else:
            self._ask_confirm(choice.upper(), choice)

    def _choose_pain(self, choice: str) -> None:
        if choice == "Back":
            self._go(MAIN, MAIN_OPTIONS, "Choose a message")
        else:
            self._ask_confirm(f"PAIN {choice}/10",
                              f"My pain is {choice} out of 10")

    def _choose_confirm(self, choice: str) -> str | None:
        if choice == "Confirm":
            self._go(MAIN, MAIN_OPTIONS, self._pending_phrase)
            return self._pending_phrase
        self._go(MAIN, MAIN_OPTIONS, "Cancelled")
        return None

    def _ask_confirm(self, label: str, phrase: str) -> None:
        self._pending_label = label
        self._pending_phrase = phrase
        self._go(CONFIRM, CONFIRM_OPTIONS, f"Send {label}?")

    def _go(self, state: str, options: list[str], message: str) -> None:
        self.state = state
        self.message = message
        self.scanner.set_options(options)
