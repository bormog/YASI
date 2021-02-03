import unittest

from lexer import Lexer
from parser import Parser
import nodes
from tests.helpers import cases


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
        for column in node.result:
            with self.subTest(column=column):
                self.assertIsInstance(column, nodes.Column)

        self.assertIsInstance(node.where, list)
        for assignee in node.where:
            with self.subTest(assignee=assignee):
                self.assertIsInstance(assignee, nodes.Assign)

        self.assertTrue(isinstance(node.order, (nodes.Empty, nodes.Order)))
        self.assertTrue(isinstance(node.limit, (nodes.Empty, nodes.Number)))



