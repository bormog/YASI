import unittest

from lexer import Lexer, LexerException
from tests.helpers import cases
from tokens import TokenType


class TestLexer(unittest.TestCase):

    def test_skip_whitespaces(self):
        text = "     "

        lex = Lexer(text)
        tokens = list(lex)
        self.assertEqual(1, len(tokens))
        self.assertEqual(TokenType.EOF, tokens.pop().type)

    def test_unknown_symbol(self):
        text = "@foobar"
        lex = Lexer(text)

        with self.assertRaises(LexerException):
            list(lex)

    @cases([
        ('create', TokenType.CREATE),
        ('table', TokenType.TABLE),
        ('primary', TokenType.PRIMARY),
        ('key', TokenType.KEY),
        ('describe', TokenType.DESCRIBE),
        ('insert', TokenType.INSERT),
        ('into', TokenType.INTO),
        ('set', TokenType.SET),
        ('select', TokenType.SELECT),
        ('from', TokenType.FROM),
        ('where', TokenType.WHERE),
        ('limit', TokenType.LIMIT),
        ('order', TokenType.ORDER),
        ('by', TokenType.BY),
        ('asc', TokenType.ASC),
        ('desc', TokenType.DESC),
        ('foobar', TokenType.ID),
        ('100500', TokenType.INT),
        ("'foo'", TokenType.STRING),
        ('(', TokenType.LPAREN),
        (')', TokenType.RPAREN),
        (',', TokenType.COMMA),
        (';', TokenType.SEMICOLON),
        ('and', TokenType.AND),
        ('=', TokenType.EQUALS),
        ('+', TokenType.PLUS),
        ('-', TokenType.MINUS),
        ('*', TokenType.MUL),
        ('/', TokenType.DIV),
    ])
    def test_lex(self, text, expected_token_type):
        lex = Lexer(text)
        token = next(iter(lex))
        self.assertEqual(text, token.value)
        self.assertEqual(expected_token_type, token.type)
