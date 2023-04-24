"""Parser of sentences (not working yet)"""

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

    def __init__(self, msg: str, index: int) -> None:
        self.index = index
        super().__init__(f'{msg} in {self.index}')

class InvalidSyntaxError(GenericParseError):
    """Illegal char error"""

    NAME = 'InvalidSyntaxError'

    def __init__(self, msg: str, token: Token|None) -> None:
        self.token = token

        if token is not None:
            msg = f'{msg} in {token.position}'

            if token.length != 1:
                msg += f', length: {token.length}'

        super().__init__(msg)

class Lexer:
    """Tokenize the sentence"""

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

    def make_tokens(self):
        """Get all tokens of sentence"""

        tokens = []

        while self.current_char is not None:
            if self.current_char in DIGITS:
                tokens.append(self.make_numbers())
                continue

            elif self.current_char.lower() in ALPHABET:
                tokens.append(self.make_var())
                continue

            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, self.index))
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, self.index))
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, self.index))
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, self.index))
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, self.index))
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, self.index))
            elif self.current_char == ',':
                tokens.append(Token(TT_SEP, self.index))
            elif self.current_char == '^':
                tokens.append(Token(TT_POWER, self.index))
            elif self.current_char == ':':
                tokens.append(Token(TT_DEF, self.index))
            elif self.current_char != ' ':
                raise IllegalCharError(f"Unexpected char: '{self.current_char}'", index=self.index)

            self.advance()

        tokens.append(Token(TT_EOF, self.index))
        return tokens

    def make_numbers(self):
        """Create number token (INT and FLOAT)"""

        num_str = ''
        dot_count = 0
        position = self.index

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, position, int(num_str), length=len(num_str))
        else:
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
    def __init__(self, name: Token, value: GenericNode) -> None:
        self.name = name
        self.value = value

    def __str__(self) -> str:
        return f"[{self.name}: {self.value}]"

class Parser:
    """Create AST to parser the math sentences"""
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
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
            elif expr is None:
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

    def mul(self, value):
        print(value, '*', value)

class DotValue(GenericValue):
    """Crate a dot"""

    def __init__(self, dot_x: NumericValue, dot_y: NumericValue) -> None:
        self.dot_x = dot_x
        self.dot_y = dot_y

class Interpreter:
    """interpret AST to parser the math sentences"""

    NO_NAME_VARNAME = '__@no name@__'

    def __init__(self) -> None:
        self.vars: dict = {self.NO_NAME_VARNAME: []}

    def visit(self, ast) -> GenericValue | None:
        """Parse the ast and returns values, if exists"""

        if isinstance(ast, NumberNode):
            return NumericValue(ast)
        elif isinstance(ast, VariableNode):
            print('Variable', ast.token)
        elif isinstance(ast, BinaryOperatorNode):
            print('BinaryOperator', ast.left_node, ast.operator, ast.right_node)
        elif isinstance(ast, UnaryOperatorNode):
            value = NumericValue(ast.node)
            if ast.operator.value == TT_MINUS:
                value.mul(-1)
            return value
        elif isinstance(ast, DotNode):
            return DotValue(NumericValue(ast.dot_x), NumericValue(ast.dot_y))
        elif isinstance(ast, DefineNode):
            value = self.visit(ast.value)
            self.vars[ast.name.value] = value
            return value

    def parse_ast(self, ast):
        """Parse the ast, but it doesn't return"""

        self.visit(ast)

    def clear(self):
        """Clear variables"""

        self.vars = {}
