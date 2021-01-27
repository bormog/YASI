import re

from tokens import TokenType, Token

WHITESPACE_RE = re.compile(r'\s+')


class LexerException(Exception):
    pass


class Lexer:

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.regexp = Lexer.get_regexp()

    def __iter__(self):
        return self._next()

    @staticmethod
    def get_regexp() -> re.compile:
        parts = []
        for token_type in TokenType:
            if not token_type.value:
                continue
            parts.append(r'(?P<%s>%s)' % (token_type.name, token_type.value))
        return re.compile('|'.join(parts), re.MULTILINE)

    def _next(self) -> Token:
        while True:
            token = self._token()
            if token.type == TokenType.EOF:
                yield token
                return
            yield token

    def _skip_whitespace(self) -> None:
        while True:
            match = WHITESPACE_RE.match(self.text, self.pos)
            if match is None:
                break
            else:
                self.pos = match.end()

    def _token(self) -> Token:
        end = len(self.text)
        self._skip_whitespace()

        if self.pos >= end:
            return Token(TokenType.EOF, 'EOF', self.pos)

        match = self.regexp.match(self.text, self.pos)
        if match is None:
            raise LexerException('Unknown symbol at %s' % self.pos)

        self.pos = match.end()
        group_name = match.lastgroup
        return Token(getattr(TokenType, group_name), match.group(group_name), self.pos)
