# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Uses pygame-ce https://pyga.me/docs/
# Dev demo: runs Scanner + Board + speech with a FAKE "select" every few
# seconds, so the screen side can be tested before gesture input is ready.
# Close the window (or press Q - developer only) to quit.

import time

import pygame

from board import Board
from scanner import Scanner
from speech import speak

OPTIONS = ["Yes", "No", "Water", "Pain", "Bathroom", "Call caregiver"]
FAKE_SELECT_EVERY_S = 5.0


def dev_quit_pressed() -> bool:
    """Developer-only Q to quit (allowed by project rules)."""
    return pygame.key.get_pressed()[pygame.K_q]


def main() -> None:
    board = Board()
    scanner = Scanner(OPTIONS, step_s=1.5)
    clock = pygame.time.Clock()
    message = "Watching..."
    next_select = time.monotonic() + FAKE_SELECT_EVERY_S

    while board.handle_events() and not dev_quit_pressed():
        now = time.monotonic()
        index = scanner.update(now)
        if now >= next_select:            # stand-in for a real gesture
            message = scanner.select()
            speak(message)
            next_select = now + FAKE_SELECT_EVERY_S
        board.draw(OPTIONS, index, message)
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
