"""Parser of sentences (not working yet)"""

from typing import Tuple, Iterator, Union, Generator

DIGITS = '0123456789'
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

TT_INT    = 'INT'
TT_FLOAT  = 'FLOAT'
TT_PLUS   = 'PLUS'
TT_MINUS  = 'MINUS'
TT_MUL    = 'MUL'
TT_DIV    = 'DIV'
TT_POWER  = 'POWER'
TT_LPAREN = 'LP'
TT_RPAREN = 'RP'
TT_VAR    = 'VAR'
TT_EOF    = 'EOF'
TT_DEF    = 'DEF'
TT_SEP    = 'SEP'

class Token:
    """Token to parse the sentences"""
    def __init__(self, type_: str, position: int, value=None, length: int=1) -> None:
        self.type = type_
        self.value = value

        self.position = position
        self.length = length


    def __repr__(self) -> str:
        cls = self.__class__

        if self.value is not None:
            return f"{cls.__name__}({self.type!r}, {self.value!r})"
        return f"{cls.__name__}({self.type!r})"

    def __str__(self) -> str:
        if self.value is not None:
            return f"({self.type}, {self.value})"
        return f"({self.type})"

class GenericParseError(Exception):
    """Generic class to parse error"""

    NAME = None

    def __init__(self, msg: str) -> None:
        if self.NAME is not None:
            msg = f'{self.NAME}: {msg}'
        super().__init__(msg)

class IllegalCharError(GenericParseError):
    """Illegal char error"""

    NAME = 'IllegalCharError'

    def __init__(self, char: str, index: int) -> None:
        self.index = index
        self.char = char
        super().__init__(f"Unexpected char: '{char}' in {self.index}")

class InvalidSyntaxError(GenericParseError):
    """Illegal char error"""

    NAME = 'InvalidSyntaxError'

    def __init__(self, msg: str, token: Union[Token, None]) -> None:
        self.token = token

        if token is not None:
            msg = f'{msg} in {token.position}'

            if token.length != 1:
                msg += f', length: {token.length}'

        super().__init__(msg)

class UndefinedVariableError(GenericParseError):
    """Interpreter error"""

    NAME = 'UndefinedVariableError'

    def __init__(self, token: Token) -> None:
        msg = f'Undefined variable: "{token.value}"'

        super().__init__(msg)

class UnexpectedVariableTypeError(GenericParseError):
    """Interpreter error"""

    NAME = 'UnexpectedVariableTypeError'

    def __init__(self, expected_type: str, token: Token) -> None:
        msg = f'Unexpected variable type, expected {expected_type} of variable "{token.value}"'

        super().__init__(msg)

class InternalInterpreterError(GenericParseError):
    """Interpreter error"""

    NAME = 'InternalInterpreterError'

class Lexer:
    """Tokenize the sentence"""

    TOKENS_TYPES = {
        '+': TT_PLUS,
        '-': TT_MINUS,
        '*': TT_MUL,
        '/': TT_DIV,
        '(': TT_LPAREN,
        ')': TT_RPAREN,
        ',': TT_SEP,
        '^': TT_POWER,
        ':': TT_DEF
    }

    def __init__(self, sentence) -> None:
        self.sentence = sentence
        self.index = -1
        self.current_char = None
        self.advance()

    def advance(self):
        """Advance the index and update the current_char"""

        self.index += 1
        if self.index < len(self.sentence):
            self.current_char = self.sentence[self.index]
        else:
            self.current_char = None

    def make_tokens(self) -> Generator[Token, None, None]:
        """Get all tokens of sentence"""

        while self.current_char is not None:
            if self.current_char in DIGITS:
                yield self.make_numbers()

            elif self.current_char.lower() in ALPHABET:
                yield self.make_var()

            elif self.current_char in self.TOKENS_TYPES:
                yield Token(self.TOKENS_TYPES[self.current_char], self.index)
                self.advance()

            elif self.current_char == ' ':
                self.advance()

            else:
                raise IllegalCharError(self.current_char, index=self.index)

        yield Token(TT_EOF, self.index)

    def make_numbers(self):
        """Create number token (INT and FLOAT)"""

        num_str = ''
        has_dot = False
        position = self.index

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char
            self.advance()

        if has_dot == 0:
            return Token(TT_INT, position, int(num_str), length=len(num_str))

        return Token(TT_FLOAT, position, float(num_str), length=len(num_str))

    def make_var(self):
        """Create number token (VAR)"""

        var_name = ''
        position = self.index

        while self.current_char is not None and self.current_char.lower() in ALPHABET + DIGITS:
            var_name += self.current_char
            self.advance()

        return Token(TT_VAR, position, var_name, length=len(var_name))

class GenericNode:
    """Generic node of AST"""

class NumberNode(GenericNode):
    """Numeric node of AST"""

    def __init__(self, token: Token) -> None:
        self.token = token

    def __str__(self) -> str:
        return f"[{self.token}]"

class VariableNode(GenericNode):
    """Variable node of AST"""

    def __init__(self, token: Token) -> None:
        self.token = token

    def __str__(self) -> str:
        return f"[{self.token}]"

class BinaryOperatorNode(GenericNode):
    """Binary operator node of AST"""

    def __init__(self, left_node: GenericNode, operator: Token, right_node: GenericNode) -> None:
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node

    def __str__(self) -> str:
        return f"[{self.left_node},{self.operator},{self.right_node}]"

class UnaryOperatorNode(GenericNode):
    """Unary operator node of AST"""

    def __init__(self, operator: Token, node: GenericNode) -> None:
        self.operator = operator
        self.node = node

    def __str__(self) -> str:
        return f"[{self.operator},{self.node}]"

class DotNode(GenericNode):
    """Dot node of AST"""

    def __init__(self, dot_x: GenericNode, dot_y: GenericNode) -> None:
        self.dot_x = dot_x
        self.dot_y = dot_y

    def __str__(self) -> str:
        return f"[{self.dot_x},{self.dot_y}]"

class DefineNode(GenericNode):
    """Define node of AST"""

    def __init__(self, name: Token, value: GenericNode) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"[{self.name}: {self.value}]"

class Parser:
    """Create AST to parser the math sentences"""
    def __init__(self, tokens: Iterator[Token]) -> None:
        self.tokens = list(tokens)
        self.index = -1
        self.current_token = None
        self.advance()

    def advance(self):
        """Advance the index and update the current_token"""

        self.index += 1

        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def parse_sentence(self) -> GenericNode:
        """
        Try to parse the tokens of sentence
        formats:
            (VAR)(DEF)[sentence]  
            [sentence]
        """

        if len(self.tokens) >= 3 and \
            self.tokens[0].type == TT_VAR and self.tokens[1].type == TT_DEF:
            name = self.tokens[0]
            self.advance()
            self.advance()

            return DefineNode(name, self.sentence())

        return self.sentence()

    def sentence(self) -> GenericNode:
        """
        Try to parse the tokens of sentence
        formats:
            (VAR)(DEF)[expr]  
            (LPAREN) [expr] (SEP) [expr] (RPAREN)  
            (LPAREN) [expr] (RPAREN)  
            [expr]
        """

        if self.current_token is not None:
            if self.current_token.type == TT_LPAREN:
                self.advance()
                res = self.expr()

                if self.current_token.type == TT_SEP:
                    x_dot = res
                    self.advance()
                    y_dot = self.expr()

                    res = DotNode(x_dot, y_dot)

                if self.current_token.type != TT_RPAREN:
                    raise InvalidSyntaxError("Expected ')'", token=self.current_token)

                self.advance()
            else:
                res = self.expr()
        else:
            res = self.expr()

        if self.current_token is None or self.current_token.type != TT_EOF:
            raise InvalidSyntaxError("Expected '+', '-', '*', '/'", token=self.current_token)

        return res

    def expr(self) -> GenericNode:
        """Try to parse an expr in tokens, format:
        [factor] ((PLUS|MINUS) [factor])*
        """

        current = self.term()
        operator = self.current_token

        while operator is not None and operator.type in (TT_PLUS, TT_MINUS):
            self.advance()
            current = BinaryOperatorNode(current, operator, self.term())
            operator = self.current_token

        return current

    def term(self) -> GenericNode:
        """Try to parse a term in tokens, format:
        [factor] ((MUL|DIV) [factor])*
        """

        current = self.factor()
        operator = self.current_token

        while operator is not None and operator.type in (TT_MUL, TT_DIV):
            self.advance()
            current = BinaryOperatorNode(current, operator, self.factor())
            operator = self.current_token

        return current

    def factor(self) -> GenericNode:
        """Try to parse a factor in tokens, format:
        [atom] ((POWER) [factor])*
        """

        current = self.atom()
        operator = self.current_token

        if operator is not None and operator.type == TT_POWER:
            self.advance()
            current = BinaryOperatorNode(current, operator, self.factor())
            operator = self.current_token

        return current

    def atom(self):
        """Try to parse a atom in tokens, formats:
            (PLUS|MINUS) [factor]  
            (LPAREN) [expr] (RPAREN)  
            (FLOAT|INT)  
            (VAR)
        """

        if self.current_token is None or self.current_token.type == TT_EOF:
            raise InvalidSyntaxError("Unexpected factor", token=None)

        if self.current_token.type in (TT_PLUS, TT_MINUS):
            operator = self.current_token
            self.advance()
            return UnaryOperatorNode(operator, self.factor())

        if self.current_token.type == TT_LPAREN:
            self.advance()
            expr = self.expr()

            if self.current_token.type != TT_RPAREN:
                raise InvalidSyntaxError("Expected ')'", token=self.current_token)

            if expr is None:
                raise InvalidSyntaxError("Unexpected ')'", token=self.current_token)

            self.advance()
            return expr

        if self.current_token.type in (TT_FLOAT, TT_INT):
            number = NumberNode(self.current_token)
            self.advance()
            return number

        if self.current_token.type == TT_VAR:
            var = VariableNode(self.current_token)
            self.advance()
            return var

        raise InvalidSyntaxError("Unexpected factor", token=self.current_token)

class GenericValue:
    """Generic value to handle values"""

class NumericValue(GenericValue):
    """Create a numeric value"""

    def __init__(self, value: GenericNode) -> None:
        self.value = value

    def get_value(self, interpreter: 'Interpreter'):
        """Get the value of dot"""
        return self._visit(self.value, interpreter)

    def _visit(self, node: GenericNode, interpreter: 'Interpreter'):
        if isinstance(node, NumberNode):
            return node.token.value

        if isinstance(node, VariableNode):
            if node.token.value not in interpreter.vars:
                raise UndefinedVariableError(node.token)

            value = interpreter.vars[node.token.value]

            if not isinstance(value, NumericValue):
                raise UnexpectedVariableTypeError('NumericValue', node.token)

            return value.get_value(interpreter)

        if isinstance(node, BinaryOperatorNode):
            left_value = self._visit(node.left_node, interpreter)
            right_value = self._visit(node.right_node, interpreter)

            if node.operator.type == TT_PLUS:
                value = left_value + right_value
            elif node.operator.type == TT_MINUS:
                value = left_value - right_value
            elif node.operator.type == TT_MUL:
                value = left_value * right_value
            elif node.operator.type == TT_DIV:
                value = left_value / right_value
            elif node.operator.type == TT_POWER:
                value = left_value ** right_value
            else:
                raise InternalInterpreterError("Unexpected node operator type")

            return value

        if isinstance(node, UnaryOperatorNode):
            value = self._visit(node.node, interpreter)

            if node.operator.type == TT_MINUS:
                value *= -1
            elif node.operator.type != TT_PLUS:
                raise InternalInterpreterError("Unexpected node operator type")

            return value

        raise InternalInterpreterError("Unexpected node type")

    def __str__(self) -> str:
        return f"<{self.value}>"

class DotValue(GenericValue):
    """Crate a dot"""

    def __init__(self, dot_x: NumericValue, dot_y: NumericValue) -> None:
        self.dot_x = dot_x
        self.dot_y = dot_y

    def get_value(self, interpreter: 'Interpreter') -> Tuple[Union[int,float], Union[int,float]]:
        """Get the value of dot"""

        return self.dot_x.get_value(interpreter), self.dot_y.get_value(interpreter)

    def __str__(self) -> str:
        return f"({self.dot_x!s}, {self.dot_y!s})"

class Interpreter:
    """interpret AST to parser the math sentences"""

    NO_NAME_VARNAME = '__@no name@__'

    def __init__(self) -> None:
        self.vars: dict = {self.NO_NAME_VARNAME: []}

    def visit(self, ast) -> GenericValue:
        """Parse the ast and returns values"""

        if isinstance(ast, DotNode):
            return DotValue(NumericValue(ast.dot_x), NumericValue(ast.dot_y))

        if isinstance(ast, DefineNode):
            value = self.visit(ast.value)
            self.vars[ast.name.value] = value
            return value

        return NumericValue(ast)

    def parse_ast(self, ast) -> None:
        """Parse the ast, but it doesn't return"""

        value = self.visit(ast)

        if isinstance(ast, DotNode):
            self.vars[self.NO_NAME_VARNAME].append(value)

    def clear(self) -> None:
        """Clear variables"""

        self.vars = {self.NO_NAME_VARNAME: []}
