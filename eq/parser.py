"""Parser of sentences (not working yet)"""

TT_INT = 'INT'
TT_PLUS = 'PLUS'

TT_VAR = 'VAR'
TT_DOT = 'DOT'

class Token:
    def __init__(self, type_, value=None) -> None:
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        cls = self.__class__

        if self.value is not None:
            return f"{cls.__name__}({self.type}, {self.value})"
        return f"{cls.__name__}({self.type})"
