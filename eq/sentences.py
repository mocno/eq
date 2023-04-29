"""This script handle the sentences and the parsers"""

from typing import TypedDict, List, Union
from . import parser

ErrorData = TypedDict('ErrorData', position=int, length=int, msg=str)

class Sentence:
    """Some mathematical sentence, this instance parses and graphs it"""
    def __init__(self, sentence: str="") -> None:
        self.sentence: str = sentence

        self.ast: Union[parser.GenericNode, None] = None
        self.parsed = False

        self.error_data: Union[ErrorData, bool] = False

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
        self.ast = None

    def pop(self, index=None):
        """Remove char of index, default index is the last char."""

        if index is None:
            self.sentence = self.sentence[:-1]
        else:
            self.sentence = self.sentence[:index] + self.sentence[index+1:]
        self.parsed = False
        self.ast = None

    def set(self, sentence: str):
        """Define new sentence and parse it"""
        self.sentence = sentence
        self.parsed = False

    def parse_ast(self):
        """Parse the sentence"""

        if not self.parsed:
            self.parsed = True

            if self.sentence != '':
                lexer = parser.Lexer(self.sentence)

                try:
                    gen_tokens = lexer.make_tokens()
                    parsed = parser.Parser(gen_tokens)
                    ast = parsed.parse_sentence()
                except parser.InvalidSyntaxError as error:
                    if error.token is not None:
                        self.error_data = ErrorData(
                            position=error.token.position,
                            length=error.token.length,
                            msg=str(error)
                        )
                    else:
                        self.error_data = True

                    print(self.error_data)
                    return
                except parser.IllegalCharError as error:
                    self.error_data = ErrorData(
                        position=error.index,
                        length=1,
                        msg=str(error)
                    )

                    print(self.error_data)
                    return

                self.ast = ast
                self.error_data = False

class Universe:
    """Universe instance, handle the sentences."""

    def __init__(self) -> None:
        self.sentences: List[Sentence] = [Sentence()]
        self.selected: int = 0
        self.interpreter = parser.Interpreter()

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
        self.sentences[self.selected].parse_ast()
        self.interpret_asts()

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
        self.sentences[self.selected].parse_ast()

        self.interpret_asts()

        self.selected += 1
        self.sentences.insert(self.selected, Sentence(after_index))

    def interpret_asts(self):
        """Generates an interpreter and interpreter the ast's"""
        self.interpreter.clear()
        for sentence in self.sentences:
            if sentence.ast is not None:
                self.interpreter.parse_ast(sentence.ast)
