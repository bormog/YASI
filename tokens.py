from enum import Enum


class TokenType(Enum):
    CREATE = r'create'
    TABLE = r'table'
    PRIMARY = r'primary'
    KEY = r'key'

    DESCRIBE = r'describe'

    INSERT = r'insert'
    INTO = r'into'
    SET = r'set'

    SELECT = r'select'
    FROM = r'from'
    WHERE = r'where'
    LIMIT = r'limit'
    ORDER = r'order'
    BY = r'by'
    ASC = r'asc'
    DESC = r'desc'

    AND = r'and'

    ID = r'[a-zA-Z_]+\d*'
    INT = r'\d+'
    STRING = r"'[^']*'"

    LPAREN = r'\('
    RPAREN = r'\)'
    COMMA = r','
    SEMICOLON = r';'
    EQUALS = r'='

    PLUS = r'\+'
    MINUS = r'-'
    MUL = r'\*'
    DIV = r'/'

    EOF = None


class Token:

    def __init__(self, token_type: TokenType, value: str, position: int):
        self._token_type = token_type
        self._value = value
        self._position = position

    @property
    def type(self):
        return self._token_type

    @property
    def value(self):
        return self._value

    @property
    def pos(self):
        return self._position

    def __repr__(self):
        return "['{value}', {type}]".format(value=self.value, type=self.type)

    def __str__(self):
        return self.__repr__()
