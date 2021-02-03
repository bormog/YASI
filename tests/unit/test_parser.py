import unittest

from lexer import Lexer
from parser import Parser
import nodes
from tests.helpers import cases


class TestSelect(unittest.TestCase):

    @cases([
        "select 1;",
        "select 1+1;"
    ])
    def test_select_expression(self, sql):
        parser = Parser(lex=Lexer(sql))
        statements = parser.parse()
        node = statements.children[0]

        self.assertIsInstance(node, nodes.SelectStatement)

        self.assertIsInstance(node.table, nodes.Empty)
        self.assertTrue(isinstance(node.result, (nodes.Number, nodes.BinaryOperation)))
        self.assertEqual(node.where, None)
        self.assertIsInstance(node.order, nodes.Empty)
        self.assertIsInstance(node.limit, nodes.Empty)

    @cases([
        "select a, b from foo;",
        "select a, b from foo where a=1;",
        "select a, b from foo where a=1 order by a asc;",
        "select a, b from foo where a=1 order by a desc;"
        "select a, b from foo where a=1 order by a asc limit 1;"
    ])
    def test_select_from(self, sql):
        parser = Parser(lex=Lexer(sql))
        statements = parser.parse()
        node = statements.children[0]

        self.assertIsInstance(node, nodes.SelectStatement)

        self.assertIsInstance(node.table, nodes.Table)
        self.assertIsInstance(node.result, list)
        self.assertIsInstance(node.where, list)

        self.assertTrue(isinstance(node.order, (nodes.Empty, nodes.Order)))
        self.assertTrue(isinstance(node.limit, (nodes.Empty, nodes.Number)))



