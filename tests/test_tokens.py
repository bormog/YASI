import unittest
from tokens import TokenType, Token


class TestTokenType(unittest.TestCase):

    def test_eof_is_ok(self):
        self.assertEqual(TokenType.EOF.value, None)

    def test_type_has_re(self):
        for token_type in TokenType:
            if token_type == TokenType.EOF:
                continue
            with self.subTest(token_type=token_type):
                self.assertIsNotNone(token_type.value)


class TestToken(unittest.TestCase):

    def test_token(self):
        token = Token(TokenType.INT, "42", 100500)
        self.assertEqual(token.type, TokenType.INT)
        self.assertEqual(token.value, "42")
        self.assertEqual(token.pos, 100500)

    def test_property_type(self):
        token = Token(TokenType.INT, "42", 0)
        with self.assertRaises(AttributeError):
            token.type = TokenType.STRING

    def test_property_value(self):
        token = Token(TokenType.INT, "42", 0)
        with self.assertRaises(AttributeError):
            token.value = "100500"
