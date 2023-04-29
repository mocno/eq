"""This script creates a screen to graph some simple math sentences"""

from typing import Union, Tuple
import pygame
from . import sentences
from . import parser

class DrawGraph:
    """Class to draw the universe"""

    GRID_SIZE = 1

    def __init__(self, canvas: pygame.Surface, universe: sentences.Universe, \
                 graph_position: pygame.Vector2, graph_scale: float) -> None:
        self.canvas = canvas
        self.universe = universe
        self.graph_position = graph_position
        self.graph_scale = graph_scale

    def draw_grid(self, canvas_position: Union[pygame.Rect, Tuple]):
        """Draw the grid"""
        canvas_x, canvas_y, width, height = canvas_position

        pygame.draw.rect(self.canvas, 'white', canvas_position)

        grid_size = int(self.GRID_SIZE * self.graph_scale)
        origin_position = -self.graph_position * self.graph_scale
        origin_position.x, origin_position.y = int(origin_position.x), int(origin_position.y)

        for grid_x in range(int(origin_position.x) % grid_size, canvas_x+width, grid_size):
            if grid_x == origin_position.x:
                pygame.draw.line(self.canvas, 'black', (grid_x, canvas_y), \
                                 (grid_x, canvas_y+height), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (grid_x, canvas_y), (grid_x, canvas_y+height))

        for grid_y in range(int(origin_position.y) % grid_size, canvas_y + height, grid_size):
            if grid_y == origin_position.y:
                pygame.draw.line(self.canvas, 'black', (canvas_x, grid_y), \
                                 (canvas_x + width, grid_y), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (canvas_x, grid_y), (canvas_x+width, grid_y))

    def draw(self, canvas_position: pygame.Rect|tuple, graph_scale: float):
        """Draw the elements in canvas"""

        self.graph_scale = graph_scale

        self.draw_grid(canvas_position)

        for name, value in self.universe.interpreter.vars.items():
            if name == self.universe.interpreter.NO_NAME_VARNAME:
                for value_without_name in value:
                    if isinstance(value_without_name, parser.DotValue):
                        self._draw_point(value_without_name, canvas_position)
            else:
                if isinstance(value, parser.DotValue):
                    self._draw_point(value, canvas_position)

    def _draw_point(self, variable: parser.DotValue, canvas_position: Union[pygame.Rect, Tuple]):
        try:
            dot_x, dot_y = variable.get_value(self.universe.interpreter)
        except (parser.UndefinedVariableError, parser.UnexpectedVariableTypeError) as error:
            print(error)
            return

        canvas_x, canvas_y, width, height = canvas_position

        if 0 < (dot_x- self.graph_position.x) * self.graph_scale - canvas_x < width and \
            0 < -(dot_y+self.graph_position.y) * self.graph_scale - canvas_y < height:
            pygame.draw.circle(self.canvas, 'red', \
                (((dot_x,-dot_y) - self.graph_position) * self.graph_scale), 4)


class Screen:
    """The screen instance, used to manage the pygame canvas"""

    FPS = 30

    def __init__(self, width: int, height: int):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Eq")

        self.canvas: pygame.Surface = pygame.display.set_mode((width, height), \
                                                              pygame.constants.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.SysFont('mono', 30)

        self.running: bool = False

        self.universe: sentences.Universe = sentences.Universe()

        self.graph_scale: float = 100
        self.graph_position: pygame.Vector2 = pygame.Vector2(-width / 2 - 200, -height / 2) \
            / self.graph_scale

        self.sentence_cursor_pos: int = 0
        self.dragging = None

        self.draw_universe: DrawGraph = DrawGraph(self.canvas, self.universe, \
                                                        self.graph_position, self.graph_scale)

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
                if 150 > new_scale > 10:
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
            event.unicode.isalpha() or event.unicode.isnumeric() or \
            event.unicode in '=-+*/^><(),: '
        ):
            char = event.unicode

            if char == '²':
                char = '^2'
                self.universe.get_selected().append(char, self.sentence_cursor_pos)
                self.sentence_cursor_pos += 2
            elif char == '³':
                char = '^3'
                self.universe.get_selected().append(char, self.sentence_cursor_pos)
                self.sentence_cursor_pos += 2
            else:
                self.universe.get_selected().append(char, self.sentence_cursor_pos)
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
        self.draw_universe.draw(rect, self.graph_scale)
