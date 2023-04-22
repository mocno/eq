""""""

import re
import pygame
from . import parser

# temp regex
DOT_RE = re.compile(r'^\((?P<x>\d+),(?P<y>\d+)\)$')

class Sentence:
    """Some mathematical sentence, this instance parses and graphs it"""
    def __init__(self, sentence: str="") -> None:
        self.sentence = sentence
        self.parsed = False
        self.error_data: bool|dict[str,int] = False

    def __str__(self):
        return self.sentence

    def __len__(self):
        return len(self.sentence)

    def __add__(self, other: 'Sentence') -> 'Sentence':
        cls = __class__
        return cls(self.sentence + other.sentence)

    def append(self, content, index):
        """Add chars of content in index."""

        self.sentence = self.sentence[:index] + content + self.sentence[index:]
        self.parsed = False

    def pop(self, index=None):
        """Remove char of index, default index is the last char."""

        if index is None:
            self.sentence = self.sentence[:-1]
        else:
            self.sentence = self.sentence[:index] + self.sentence[index+1:]
        self.parsed = False

    def set(self, sentence: str):
        """Define new sentence and parse it"""
        self.sentence = sentence
        self.parse()

    def parse(self):
        """Parse the sentence"""

        if not self.parsed:
            self.parsed = True

            if self.sentence != '':
                print('parsing:', self.sentence)

                lexer = parser.Lexer(self.sentence)

                try:
                    tokens = lexer.make_tokens()
                except parser.IllegalCharError as error:
                    print("Error", error.index)
                    self.error_data = { 'position': error.index, 'length': 1 }
                    return

                try:
                    parsed = parser.Parser(tokens)
                    ast = parsed.parse()
                except parser.InvalidSyntaxError as error:
                    print("Error", error)
                    if error.token is not None:
                        self.error_data = { 'position': error.token.position, 'length': error.token.length }
                    else:
                        self.error_data = True
                    return

                print(ast)

                self.error_data = False

    def draw(self, canvas: pygame.Surface, canvas_position: pygame.Rect|tuple, \
             graph_position: pygame.Vector2, graph_scale: float):
        """Draw the element in canvas"""

class Universe:
    """Universe instance, handle the sentences."""

    def __init__(self) -> None:
        self.sentences: list[Sentence] = [Sentence()]
        self.selected: int = 0

    def __iter__(self):
        yield from self.sentences

    def __len__(self):
        return len(self.sentences)

    def select(self, index: int):
        """Set selected sentence by index. If unexpected index, nothing happens."""

        if 0 <= index < len(self):
            self.selected = index

    def get_selected(self):
        """Get selected sentence."""

        return self.sentences[self.selected]


    def pop_selected(self):
        """Pop the selected sentence, if it only have one sentence nothing happens"""

        if len(self.sentences) != 1:
            self.sentences.pop(self.selected)

            if self.selected != 0:
                self.selected -= 1

    def parse_selected(self):
        """Parse the selected sentence"""

        self.sentences[self.selected].parse()

    def join_with_next(self):
        """
        Join the selected sentence with the next sentence, removing the next one.
        Only if the selected element is not the last sentence
        """

        if self.selected != len(self)-1:
            self.sentences[self.selected] += self.sentences[self.selected +1]
            self.sentences.pop(self.selected +1)

    def split_selected(self, index: int):
        """Split the selected sentence, creating another phrase with the surplus"""

        before_index = self.sentences[self.selected].sentence[:index]
        after_index  = self.sentences[self.selected].sentence[index:]

        self.sentences[self.selected].set(before_index)

        self.selected += 1
        self.sentences.insert(self.selected, Sentence(after_index))
