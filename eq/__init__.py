"""This script creates a screen to graph some simple math sentences"""

import pygame
from .sentences import Universe

class Screen:
    """The screen instance, used to manage the pygame canvas"""

    FPS = 30
    GRID_SIZE = 5

    def __init__(self, width: int, height: int):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Eq")

        self.canvas: pygame.Surface = pygame.display.set_mode((width, height), \
                                                              pygame.constants.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.SysFont('mono', 30)

        self.running: bool = False

        self.universe: Universe = Universe()

        self.graph_scale: float = 20
        self.graph_position: pygame.Vector2 = pygame.Vector2(-width / 2 - 200, -height / 2) \
            / self.graph_scale

        self.sentence_cursor_pos: int = 0
        self.dragging = None

        self.universe.get_selected().append("1+x^2/3", 0)

    def __repr__(self) -> str:
        cls = self.__class__

        return f"{cls.__name__}({self.canvas.get_width()}, {self.canvas.get_height()})"

    def start(self):
        """Start the screen"""

        self.running = True

        while self.running:
            self._lister_events()
            self._draw()
            self.clock.tick(self.FPS)

    def _lister_events(self):
        for event in pygame.event.get():
            if event.type == pygame.constants.QUIT:
                self.running = False
            elif event.type == pygame.constants.KEYDOWN:
                self.on_keydown(event)

            elif event.type == pygame.constants.MOUSEWHEEL:
                new_scale = self.graph_scale + event.y * self.graph_scale / 10
                if 100 > new_scale > 5:
                    self.graph_scale = new_scale

            elif event.type == pygame.constants.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = { 'last_pos': event.pos }

            elif event.type == pygame.constants.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = None

            elif event.type == pygame.constants.MOUSEMOTION:
                if self.dragging is not None:
                    self.graph_position += (
                        (self.dragging['last_pos'][0] - event.pos[0]) / self.graph_scale,
                        (self.dragging['last_pos'][1] - event.pos[1]) / self.graph_scale
                    )
                    self.dragging['last_pos'] = event.pos

    def on_keydown(self, event):
        """Handle keydown events"""

        if event.key == pygame.constants.K_ESCAPE:
            self.running = False

        elif event.key == pygame.constants.K_HOME:
            self.sentence_cursor_pos = 0

        elif event.key == pygame.constants.K_END:
            self.sentence_cursor_pos = len(self.universe.get_selected())

        elif event.key == pygame.constants.K_DOWN:
            if event.mod & pygame.constants.KMOD_CTRL:
                self.universe.select(len(self.universe) -1)
            else:
                self.universe.parse_selected()
                self.universe.select(self.universe.selected+1)
            self.sentence_cursor_pos = min( \
                len(self.universe.get_selected()), self.sentence_cursor_pos)

        elif event.key == pygame.constants.K_UP:
            if event.mod & pygame.constants.KMOD_CTRL:
                self.universe.selected = 0
            else:
                self.universe.parse_selected()
                self.universe.select(self.universe.selected-1)
            self.sentence_cursor_pos = min( \
                len(self.universe.get_selected()), self.sentence_cursor_pos)

        elif event.key == pygame.constants.K_LEFT:
            if event.mod & pygame.constants.KMOD_CTRL:
                self.sentence_cursor_pos = 0
            elif self.sentence_cursor_pos > 0:
                self.sentence_cursor_pos -= 1
            else:
                self.universe.parse_selected()
                self.universe.select(self.universe.selected-1)
                self.sentence_cursor_pos = len(self.universe.get_selected())

        elif event.key == pygame.constants.K_RIGHT:
            if event.mod & pygame.constants.KMOD_CTRL:
                self.sentence_cursor_pos = len(self.universe.get_selected())
            elif self.sentence_cursor_pos < len(self.universe.get_selected()):
                self.sentence_cursor_pos += 1
            else:
                self.universe.parse_selected()
                self.universe.select(self.universe.selected+1)
                self.sentence_cursor_pos = len(self.universe.get_selected())

        elif event.key == pygame.constants.K_BACKSPACE:
            if self.sentence_cursor_pos != 0:
                self.sentence_cursor_pos -= 1
                self.universe.get_selected().pop(self.sentence_cursor_pos)
            else:
                self.universe.select(self.universe.selected-1)
                self.sentence_cursor_pos = len(self.universe.get_selected())
                self.universe.join_with_next()

        elif event.key == pygame.constants.K_DELETE:
            if len(self.universe.get_selected()) != self.sentence_cursor_pos:
                self.universe.get_selected().pop(self.sentence_cursor_pos)
            else:
                self.universe.join_with_next()

        elif event.key == pygame.constants.K_RETURN:
            self.universe.split_selected(self.sentence_cursor_pos)
            self.sentence_cursor_pos = 0

        elif event.unicode != '' and ( \
            event.unicode.isalpha() or event.unicode.isnumeric() or event.unicode in '=-+*/^><(),' \
        ):
            self.universe.get_selected().append(event.unicode, self.sentence_cursor_pos)
            self.sentence_cursor_pos += 1

    def _draw(self):
        window_width, window_height = self.canvas.get_width(), self.canvas.get_height()
        sentence_tab_width = min(400, int(window_width / 2))

        self.canvas.fill('white')

        self._draw_graph(pygame.Rect(0, 0, window_width, window_height))
        self._draw_sentences_tab((0, 0, sentence_tab_width, window_height))

        pygame.display.update()
        pygame.display.flip()

    def _draw_sentences_tab(self, rect):
        tab_x, tab_y, width, height = rect

        pygame.draw.rect(self.canvas, 'black', rect)
        pygame.draw.rect(self.canvas, 'white', (tab_x +2, tab_y +2, width -4, height -4))

        pygame.draw.rect(self.canvas, 'gray', (10, tab_y + 40 * self.universe.selected + 20, 5, 30))

        before_cursor_content = str(self.universe.get_selected())[:self.sentence_cursor_pos]
        cursor_pos = self.font.render(before_cursor_content, False, 'black').get_width()
        cursor_position = (cursor_pos +20, tab_y + 40 * self.universe.selected + 20, 2, 30)
        pygame.draw.rect(self.canvas, 'gray', cursor_position)

        for index, sentence in enumerate(self.universe):
            text = str(sentence)

            if sentence.error_data is not False:
                if isinstance(sentence.error_data, dict) and \
                   sentence.error_data['position'] < len(text):
                    before_error = text[:sentence.error_data['position']]
                    error_x = self.font.render(before_error, False, 'black').get_width()

                    error_content = text[
                        sentence.error_data['position']: \
                        sentence.error_data['position']+sentence.error_data['length']
                    ]
                    error_width = self.font.render(error_content, False, 'black').get_width()

                    error_position = (error_x +20, tab_y + 40 * index + 52, error_width, 3)
                else:
                    error_position = (7, tab_y + 40 * index + 20, 2, 30)

                pygame.draw.rect(self.canvas, 'red', error_position)

            text = self.font.render(text, True, 'black')
            self.canvas.blit(text, (tab_x + 20, tab_y + 40 * index + 20))


    def _draw_graph(self, rect: pygame.Rect):
        pygame.draw.rect(self.canvas, 'white', rect)

        grid_size = int(self.GRID_SIZE * self.graph_scale)
        origin_position = -self.graph_position * self.graph_scale
        origin_position.x, origin_position.y = int(origin_position.x), int(origin_position.y)

        for grid_x in range(int(origin_position.x) % grid_size, rect.right, grid_size):
            if grid_x == origin_position.x:
                pygame.draw.line(self.canvas, 'black', (grid_x, rect.top), (grid_x, rect.bottom), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (grid_x, rect.top), (grid_x, rect.bottom))

        for grid_y in range(int(origin_position.y) % grid_size, rect.bottom, grid_size):
            if grid_y == origin_position.y:
                pygame.draw.line(self.canvas, 'black', (rect.left, grid_y), (rect.right, grid_y), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (rect.left, grid_y), (rect.right, grid_y))

        for sentence in self.universe:
            sentence.draw(self.canvas, rect, self.graph_position, self.graph_scale)
