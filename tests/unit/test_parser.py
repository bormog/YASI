import unittest

from lexer import Lexer
from parser import Parser
import nodes
from tests.helpers import cases


class TestParser(unittest.TestCase):

    @cases([
        ("42", nodes.Number),
        ("(42)", nodes.Number),
        ("2+2", nodes.BinaryOperation),
        ("2+3+4", nodes.BinaryOperation),
        ("2*3", nodes.BinaryOperation),
        ("2*3*4", nodes.BinaryOperation),
    ])
    def test_expr(self, text, expected):
        parser = Parser(lex=Lexer(text))
        node = parser.expr()
        self.assertIsInstance(node, expected)

    @cases([
        ("42", nodes.Number),
        ("(42)", nodes.Number),
        ("2*3", nodes.BinaryOperation),
        ("2*3*4", nodes.BinaryOperation),
    ])
    def test_term(self, text, expected):
        parser = Parser(lex=Lexer(text))
        node = parser.term()
        self.assertIsInstance(node, expected)

    @cases([
        "100500",
        "(100500)"
    ])
    def test_factor_int(self, text):
        parser = Parser(lex=Lexer(text))
        node = parser.factor()
        self.assertIsInstance(node, nodes.Number)

    @cases([
        "0",
        "42",
    ])
    def test_value_num(self, text):
        parser = Parser(lex=Lexer(text))
        node = parser.value()
        self.assertIsInstance(node, nodes.Number)

    @cases([
        "'foo'",
        "'foo_bar"
        "'",
    ])
    def test_value_str(self, text):
        parser = Parser(lex=Lexer(text))
        node = parser.value()
        self.assertIsInstance(node, nodes.String)

    @cases([
        "order by foo asc",
        "order by foo desc"
    ])
    def test_order(self, text):
        parser = Parser(lex=Lexer(text))
        node = parser.order_sub_stmt()
        self.assertIsInstance(node, nodes.Order)
        self.assertIsInstance(node.column, nodes.Column)

    def test_limit(self):
        parser = Parser(lex=Lexer("limit 10"))
        node = parser.limit_sub_stmt()
        self.assertIsInstance(node, nodes.Number)

    @cases([
        "foo=42",
        "foo='bar'"
    ])
    def test_assignee(self, text):
        parser = Parser(lex=Lexer(text))
        node = parser.assignee_sub_stmt()
        self.assertIsInstance(node, nodes.Assign)
        self.assertIsInstance(node.left, nodes.Column)


class TestCreate(unittest.TestCase):

    @cases([
        "create table foo (primary key foo);",
        "create table foo (primary key foo, bar);"
    ])
    def test_create_statement(self, sql):
        parser = Parser(lex=Lexer(sql))
        statements = parser.parse()
        node = statements.children[0]

        self.assertIsInstance(node, nodes.CreateStatement)
        self.assertIsInstance(node.table, nodes.Table)
        self.assertIsInstance(node.primary_key, nodes.Column)

        for column in node.columns:
            with self.subTest(column=column):
                self.assertIsInstance(column, nodes.Column)


class TestDescribe(unittest.TestCase):

    def test_describe_statement(self):
        sql = "describe foo;"
        parser = Parser(lex=Lexer(sql))
        statements = parser.parse()
        node = statements.children[0]

        self.assertIsInstance(node, nodes.DescribeStatement)
        self.assertIsInstance(node.table, nodes.Table)


class TestInsert(unittest.TestCase):

    def test_describe_statement(self):
        sql = "insert into foo set a=1, b=2, c='3';"
        parser = Parser(lex=Lexer(sql))
        statements = parser.parse()
        node = statements.children[0]

        self.assertIsInstance(node, nodes.InsertStatement)
        self.assertIsInstance(node.table, nodes.Table)

        for assignee in node.assignments:
            with self.subTest(assignee=assignee):
                self.assertIsInstance(assignee, nodes.Assign)


class TestSelect(unittest.TestCase):

    @cases([
        "select 1;",
        "select 1+1;",
        "select 2*3;",
        "select ((1+1)*(2+2));"
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
        for column in node.result:
            with self.subTest(column=column):
                self.assertIsInstance(column, nodes.Column)

        self.assertIsInstance(node.where, list)
        for assignee in node.where:
            with self.subTest(assignee=assignee):
                self.assertIsInstance(assignee, nodes.Assign)

        self.assertTrue(isinstance(node.order, (nodes.Empty, nodes.Order)))
        self.assertTrue(isinstance(node.limit, (nodes.Empty, nodes.Number)))



