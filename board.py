# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Uses pygame-ce for drawing https://pyga.me/docs/
# The needs board screen. It is display-only: mouse and keyboard events are
# ignored (competition rule); only closing the window is handled.

import pygame

BG = (0, 0, 0)
BOX = (40, 40, 40)
TEXT = (255, 255, 255)
HIGHLIGHT = (255, 220, 0)        # bright yellow on black = high contrast
HIGHLIGHT_TEXT = (0, 0, 0)
MESSAGE_BG = (0, 70, 140)

COLS = 3
MARGIN = 20
MESSAGE_H = 160


class Board:
    """A window that shows the options grid and a message bar."""

    def __init__(self, size: tuple[int, int] = (1200, 800)) -> None:
        pygame.init()
        pygame.display.set_caption("SignalSpeak")
        self.screen = pygame.display.set_mode(size)
        self.option_font = pygame.font.SysFont("arial", 64, bold=True)
        self.message_font = pygame.font.SysFont("arial", 72, bold=True)

    def handle_events(self) -> bool:
        """Drain events. Returns False when the window is closed."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True                       # all mouse/keyboard input ignored

    def draw(self, options: list[str], highlighted_index: int,
             message: str) -> None:
        """Draw the whole screen for one frame."""
        self.screen.fill(BG)
        for i, option in enumerate(options):
            rect = self._box_rect(i, len(options))
            self._draw_box(rect, option, i == highlighted_index)
        self._draw_message(message)
        pygame.display.flip()

    def _box_rect(self, i: int, count: int) -> pygame.Rect:
        """Grid position of option i."""
        width, height = self.screen.get_size()
        rows = (count + COLS - 1) // COLS
        box_w = (width - MARGIN * (COLS + 1)) // COLS
        box_h = (height - MESSAGE_H - MARGIN * (rows + 2)) // rows
        col, row = i % COLS, i // COLS
        x = MARGIN + col * (box_w + MARGIN)
        y = MARGIN + row * (box_h + MARGIN)
        return pygame.Rect(x, y, box_w, box_h)

    def _draw_box(self, rect: pygame.Rect, label: str,
                  highlighted: bool) -> None:
        """One option box; the highlighted one is yellow with a thick border."""
        fill = HIGHLIGHT if highlighted else BOX
        color = HIGHLIGHT_TEXT if highlighted else TEXT
        pygame.draw.rect(self.screen, fill, rect, border_radius=16)
        if highlighted:
            pygame.draw.rect(self.screen, TEXT, rect, width=10,
                             border_radius=16)
        self._blit_centered(self.option_font, label, color, rect)

    def _draw_message(self, message: str) -> None:
        """The big bar at the bottom showing what was selected."""
        width, height = self.screen.get_size()
        rect = pygame.Rect(MARGIN, height - MESSAGE_H - MARGIN,
                           width - 2 * MARGIN, MESSAGE_H)
        pygame.draw.rect(self.screen, MESSAGE_BG, rect, border_radius=16)
        self._blit_centered(self.message_font, message, TEXT, rect)

    def _blit_centered(self, font: pygame.font.Font, text: str,
                       color: tuple[int, int, int], rect: pygame.Rect) -> None:
        """Draw text centred inside rect."""
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))
