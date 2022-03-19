import enum

class Operators(enum.Enum):
    CONCAT = "•"
    OR = "|"
    OPTIONAL = "?"
    OPEN_PARENTHESES = "("
    CLOSE_PARENTHESES = ")"
    KLEENE = "*"
    PLUS = "+"

OPERATORS = {
    '|': Operators.OR,
    '?': Operators.OPTIONAL,
    '(': Operators.OPEN_PARENTHESES,
    ')': Operators.CLOSE_PARENTHESES,
    '*': Operators.KLEENE,
    '+': Operators.PLUS,
}

UNARY_OPS = {"+", "*", "?"}

PRECEDENCE = {
    Operators.CONCAT: 2,
    Operators.OR: 1,
    Operators.KLEENE: 3,
    Operators.PLUS: 3,
    Operators.OPTIONAL: 3,
    Operators.OPEN_PARENTHESES: 0,
    Operators.CLOSE_PARENTHESES: 0,
}

