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
PROGRESS = (0, 160, 0)           # dark green bar on the yellow box
PROGRESS_H = 24
ALERT_BG = (200, 0, 0)           # emergency red

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
        self.banner_font = pygame.font.SysFont("arial", 140, bold=True)

    def handle_events(self) -> bool:
        """Drain events. Returns False when the window is closed."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True                       # all mouse/keyboard input ignored

    def draw(self, options: list[str], highlighted_index: int,
             message: str, progress: float = 0.0,
             banner: str | None = None) -> None:
        """Draw the whole screen for one frame.

        progress (0..1) fills a bar along the bottom of the highlighted box
        while the user holds a gesture. banner, if given, is shown as a big
        red alert over the options.
        """
        self.screen.fill(BG)
        for i, option in enumerate(options):
            rect = self._box_rect(i, len(options))
            self._draw_box(rect, option, i == highlighted_index)
            if i == highlighted_index:
                self._draw_progress(rect, progress)
        self._draw_message(message)
        if banner:
            self._draw_banner(banner)
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

    def _draw_progress(self, rect: pygame.Rect, progress: float) -> None:
        """Bar along the bottom of a box, filled from left to right."""
        if progress <= 0:
            return
        inner = rect.inflate(-2 * MARGIN, 0)
        width = int(inner.width * min(progress, 1.0))
        bar = pygame.Rect(inner.left, rect.bottom - MARGIN - PROGRESS_H,
                          width, PROGRESS_H)
        pygame.draw.rect(self.screen, PROGRESS, bar, border_radius=8)

    def _draw_banner(self, text: str) -> None:
        """Big red alert covering the options grid."""
        width, height = self.screen.get_size()
        rect = pygame.Rect(0, 0, width, height - MESSAGE_H - 2 * MARGIN)
        pygame.draw.rect(self.screen, ALERT_BG, rect)
        pygame.draw.rect(self.screen, TEXT, rect, width=16)
        self._blit_centered(self.banner_font, text, TEXT, rect)

    def _draw_message(self, message: str) -> None:
        """The big bar at the bottom showing what was selected."""
        width, height = self.screen.get_size()
        rect = pygame.Rect(MARGIN, height - MESSAGE_H - MARGIN,
                           width - 2 * MARGIN, MESSAGE_H)
        pygame.draw.rect(self.screen, MESSAGE_BG, rect, border_radius=16)
        self._blit_centered(self.message_font, message, TEXT, rect)

    def _blit_centered(self, font: pygame.font.Font, text: str,
                       color: tuple[int, int, int], rect: pygame.Rect) -> None:
        """Draw text centred inside rect, shrinking it if it is too wide."""
        surface = font.render(text, True, color)
        max_w = rect.width - 2 * MARGIN
        if surface.get_width() > max_w:
            scale = max_w / surface.get_width()
            surface = pygame.transform.smoothscale_by(surface, scale)
        self.screen.blit(surface, surface.get_rect(center=rect.center))
