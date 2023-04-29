"""This script creates a screen to graph some simple math sentences"""

from typing import Union, Tuple
import pygame
from . import sentences
from . import parser

class DrawGraph:
    """Class to draw the universe"""

    GRID_SIZE = 1

    def __init__(self, canvas: pygame.Surface, universe: sentences.Universe, \
                 origin: pygame.Vector2, scale: float) -> None:
        self.canvas = canvas
        self.universe = universe
        self.origin = origin
        self.scale = scale

    def draw_grid(self, canvas_position: Tuple[int, int, int, int]):
        """Draw the grid"""
        canvas_x, canvas_y, width, height = canvas_position

        pygame.draw.rect(self.canvas, 'white', canvas_position)

        grid_size = int(self.GRID_SIZE * self.scale)
        origin_x, origin_y = int(self.origin.x), int(self.origin.y)

        for grid_x in range(origin_x % grid_size, canvas_x+width, grid_size):
            if grid_x == origin_x:
                pygame.draw.line(self.canvas, 'black', (grid_x, canvas_y), \
                                 (grid_x, canvas_y+height), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (grid_x, canvas_y), (grid_x, canvas_y+height))

        for grid_y in range(origin_y % grid_size, canvas_y + height, grid_size):
            if grid_y == origin_y:
                pygame.draw.line(self.canvas, 'black', (canvas_x, grid_y), \
                                 (canvas_x + width, grid_y), 2)
            else:
                pygame.draw.line(self.canvas, 'gray', (canvas_x, grid_y), (canvas_x+width, grid_y))


    def add_position(self, delta: pygame.Vector2):
        """Add value of graph position"""
        self.origin += delta

    def draw(self, canvas_position: Tuple[int, int, int, int]):
        """Draw the elements in canvas"""

        self.draw_grid(canvas_position)

        for name, value in self.universe.interpreter.vars.items():
            if name == self.universe.interpreter.NO_NAME_VARNAME:
                for value_without_name in value:
                    if isinstance(value_without_name, parser.DotValue):
                        self._draw_point(value_without_name, canvas_position)
            else:
                if isinstance(value, parser.DotValue):
                    self._draw_point(value, canvas_position)

    def _draw_point(self, variable: parser.DotValue, canvas_position: Tuple[int, int, int, int]):
        try:
            dot = variable.get_value(self.universe.interpreter)
        except (parser.UndefinedVariableError, parser.UnexpectedVariableTypeError) as error:
            print(error)
            return

        canvas_x, canvas_y, width, height = canvas_position

        dot = pygame.Vector2(dot[0],-dot[1])
        dot = dot * self.scale + self.origin

        if 0 < dot.x -canvas_x < width and 0 < dot.y -canvas_y < height:
            pygame.draw.circle(self.canvas, 'red', dot, 4)


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

        self.sentence_cursor_pos: int = 0
        self.dragging = None

        origin = pygame.Vector2(width / 2, height / 2)
        self.draw_universe: DrawGraph = DrawGraph(self.canvas, self.universe, origin, 100)

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
                new_scale = self.draw_universe.scale * (event.y / 10 + 1)

                if 150 > new_scale > 10:
                    self.draw_universe.scale = new_scale

            elif event.type == pygame.constants.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = { 'last_pos': event.pos }

            elif event.type == pygame.constants.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = None

            elif event.type == pygame.constants.MOUSEMOTION:
                if self.dragging is not None:
                    new_position = pygame.Vector2(event.pos[0], event.pos[1])
                    self.draw_universe.add_position(new_position - self.dragging['last_pos'])
                    self.dragging['last_pos'] = new_position

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

        self.draw_universe.draw((0, 0, window_width, window_height))
        self._draw_sentences_tab(pygame.Rect(0, 0, sentence_tab_width, window_height))

        pygame.display.update()
        pygame.display.flip()

    def _draw_sentences_tab(self, tab: pygame.Rect):
        pygame.draw.rect(self.canvas, 'black', tab)
        pygame.draw.rect(self.canvas, 'white', (tab.x +2, tab.y +2, tab.width -4, tab.height -4))

        pygame.draw.rect(self.canvas, 'gray', (10, tab.y + 40 * self.universe.selected + 20, 5, 30))

        before_cursor_content = str(self.universe.get_selected())[:self.sentence_cursor_pos]
        cursor_pos = self.font.render(before_cursor_content, False, 'black').get_width()
        cursor_position = (cursor_pos +20, tab.y + 40 * self.universe.selected + 20, 2, 30)
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

                    error_position = (error_x +20, tab.y + 40 * index + 52, error_width, 3)
                else:
                    error_position = (7, tab.y + 40 * index + 20, 2, 30)

                pygame.draw.rect(self.canvas, 'red', error_position)

            text = self.font.render(text, True, 'black')
            self.canvas.blit(text, (tab.x + 20, tab.y + 40 * index + 20))
