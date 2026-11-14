# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Uses pygame-ce https://pyga.me/docs/
# Dev demo: runs Scanner + Flow + Board + speech with a FAKE "select" every
# few seconds, so the screen side can be tested before gesture input is
# ready. Close the window (or press Q - developer only) to quit.

import time

import pygame

from board import Board
from flow import Flow
from scanner import Scanner
from speech import speak

FAKE_SELECT_EVERY_S = 5.0


def dev_quit_pressed() -> bool:
    """Developer-only Q to quit (allowed by project rules)."""
    return pygame.key.get_pressed()[pygame.K_q]


def main() -> None:
    board = Board()
    flow = Flow(Scanner(["..."], step_s=1.5))
    clock = pygame.time.Clock()
    next_select = time.monotonic() + FAKE_SELECT_EVERY_S

    while board.handle_events() and not dev_quit_pressed():
        now = time.monotonic()
        index = flow.scanner.update(now)
        if now >= next_select:            # stand-in for a real gesture
            phrase = flow.select()
            if phrase:
                speak(phrase)
            next_select = now + FAKE_SELECT_EVERY_S
        board.draw(flow.options, index, flow.message)
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
