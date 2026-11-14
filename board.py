# Written with help from Claude Code (Anthropic); colours, font, text
# fitting, progress bar and alert banner revised with Claude - see
# AI_USAGE.md.
# Uses pygame-ce for drawing https://pyga.me/docs/
# The needs board screen. It is display-only: mouse and keyboard events are
# ignored (competition rule); only closing the window is handled.

import pygame

BG = (74, 44, 32)                  # dark chocolate brown
BOX = (240, 160, 195)              # pink
TEXT = (82, 40, 26)                # chocolate brown on pink
HIGHLIGHT = (255, 220, 235)        # lighter pink = "this one is selected"
HIGHLIGHT_BORDER = (255, 244, 214) # cream outline
MESSAGE_BG = (120, 70, 50)         # lighter brown bar
MESSAGE_TEXT = (255, 214, 232)     # light pink on brown
PROGRESS = (255, 244, 214)         # cream "keep holding" bar
ALERT_BG = (200, 40, 60)           # strong red for the emergency banner
ALERT_TEXT = (255, 255, 255)

FONT_NAMES = "comicsansms,trebuchetms,arial"   # first one installed is used
OPTION_SIZE = 64
MESSAGE_SIZE = 72
MIN_SIZE = 24
TEXT_PAD = 30                      # space kept free at the sides of text

COLS = 3
MARGIN = 20
MESSAGE_H = 160
GROW = 20                          # highlighted box is this much bigger
PROGRESS_H = 14
BANNER_H = 120


class Board:
    """A window that shows the options grid and a message bar."""

    def __init__(self, size: tuple[int, int] = (1200, 800)) -> None:
        pygame.init()
        pygame.display.set_caption("SignalSpeak")
        self.screen = pygame.display.set_mode(size)
        self._fonts: dict[int, pygame.font.Font] = {}

    def handle_events(self) -> bool:
        """Drain events. Returns False when the window is closed."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True                       # all mouse/keyboard input ignored

    def draw(self, options: list[str], highlighted_index: int,
             message: str, progress: float = 0.0, banner=None) -> None:
        """Draw the whole screen for one frame.

        progress: 0..1 for how far the user has held a gesture.
        banner: text for the emergency banner, or None/'' for none.
        """
        self.screen.fill(BG)
        for i, option in enumerate(options):
            rect = self._box_rect(i, len(options))
            self._draw_box(rect, option, i == highlighted_index)
        self._draw_message(message)
        self._draw_progress(progress)
        if banner:
            self._draw_banner(str(banner))
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
        """One option box; the highlighted one is lighter, bigger, outlined."""
        if highlighted:
            rect = rect.inflate(GROW, GROW)
            pygame.draw.rect(self.screen, HIGHLIGHT, rect, border_radius=24)
            pygame.draw.rect(self.screen, HIGHLIGHT_BORDER, rect, width=10,
                             border_radius=24)
        else:
            pygame.draw.rect(self.screen, BOX, rect, border_radius=24)
        self._blit_centered(label, OPTION_SIZE, TEXT, rect)

    def _message_rect(self) -> pygame.Rect:
        width, height = self.screen.get_size()
        return pygame.Rect(MARGIN, height - MESSAGE_H - MARGIN,
                           width - 2 * MARGIN, MESSAGE_H)

    def _draw_message(self, message: str) -> None:
        """The big bar at the bottom showing what was selected."""
        rect = self._message_rect()
        pygame.draw.rect(self.screen, MESSAGE_BG, rect, border_radius=24)
        self._blit_centered(message, MESSAGE_SIZE, MESSAGE_TEXT, rect)

    def _draw_progress(self, progress: float) -> None:
        """A thin bar above the message bar that fills while a gesture is held."""
        progress = max(0.0, min(1.0, progress))
        if progress <= 0:
            return
        msg = self._message_rect()
        full = pygame.Rect(msg.x, msg.y - PROGRESS_H - 6, msg.width,
                           PROGRESS_H)
        done = pygame.Rect(full.x, full.y, int(full.width * progress),
                           full.height)
        pygame.draw.rect(self.screen, PROGRESS, done, border_radius=7)

    def _draw_banner(self, text: str) -> None:
        """Big red emergency banner across the top of the screen."""
        width = self.screen.get_width()
        rect = pygame.Rect(MARGIN, MARGIN, width - 2 * MARGIN, BANNER_H)
        pygame.draw.rect(self.screen, ALERT_BG, rect, border_radius=24)
        self._blit_centered(text, MESSAGE_SIZE, ALERT_TEXT, rect)

    def _font(self, size: int) -> pygame.font.Font:
        """Cached bold font of the given size."""
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont(FONT_NAMES, size,
                                                    bold=True)
        return self._fonts[size]

    def _fit_font(self, text: str, base_size: int,
                  max_width: int) -> pygame.font.Font:
        """Largest font (down to MIN_SIZE) in which text fits max_width."""
        for size in range(base_size, MIN_SIZE - 1, -4):
            font = self._font(size)
            if font.size(text)[0] <= max_width:
                return font
        return self._font(MIN_SIZE)

    def _blit_centered(self, text: str, base_size: int,
                       color: tuple[int, int, int],
                       rect: pygame.Rect) -> None:
        """Draw text centred inside rect, shrinking it if it is too wide."""
        font = self._fit_font(text, base_size, rect.width - 2 * TEXT_PAD)
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))