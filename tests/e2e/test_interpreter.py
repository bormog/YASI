import os
import unittest

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser
from tests.helpers import cases


class TestInterpreter(unittest.TestCase):
    TEST_DIR = 'tests_tables'

    def setUp(self) -> None:
        if not os.path.exists(self.TEST_DIR):
            os.mkdir(self.TEST_DIR)

    def tearDown(self) -> None:
        for filename in os.listdir(self.TEST_DIR):
            os.remove(os.path.join(self.TEST_DIR, filename))
        os.rmdir(self.TEST_DIR)

    @cases([
        (
                [
                    "create table foobar (primary key foo);",
                    "describe foobar;"
                ],
                [
                    True,
                    ["foo"]
                ]
        ),
        (
                [
                    "create table foo (primary key foo, bar, buz);",
                    "describe foo;"
                ],
                [
                    True,
                    ["foo", "bar", "buz"]
                ]
        ),

    ])
    def test_create_ok(self, queries, expected):
        sql = "".join(queries)
        inter = Interpreter(tree=Parser(lex=Lexer(sql)).parse(), working_dir=self.TEST_DIR)
        results = inter.do()
        self.assertEqual(expected, results)

    @cases([
        ("select 1;", [1]),
        ("select 1+1;", [2]),
        ("select 1+1+1;", [3]),
        ("select 1-1;", [0]),
        ("select 1-1-1;", [-1]),
        ("select 2*3;", [6]),
        ("select 2*3*4;", [24]),
        ("select 24/4;", [6]),
        ("select 24/4/3;", [2]),
        ("select 2*3+2*3;", [12]),
        ("select 2*3-2*3;", [0]),
        ("select 2*(3+2)*3;", [30]),
        ("select 2*(3-2)*3;", [6]),
    ])
    def test_select_expressions_ok(self, sql, expected):
        inter = Interpreter(tree=Parser(lex=Lexer(sql)).parse(), working_dir=self.TEST_DIR)
        results = inter.do()
        self.assertEqual(expected, results)

    @cases([
        (
                [
                    "create table foobar (primary key uid, a, b);",
                    "insert into foobar set uid=1, a='Hello', b=100;",
                    "select uid, a, b from foobar;"
                    "insert into foobar set uid=2, a='World', b=200;",
                    "select uid, a, b from foobar;"
                ],
                [
                    True,
                    None,
                    [[1, "Hello", 100]],
                    None,
                    [[1, "Hello", 100], [2, "World", 200]]
                ]
        ),
    ])
    def test_insert_ok(self, queries, expected):
        sql = "".join(queries)
        inter = Interpreter(tree=Parser(lex=Lexer(sql)).parse(), working_dir=self.TEST_DIR)
        results = inter.do()
        self.assertEqual(expected, results)


class TestInterpreterSelect(unittest.TestCase):
    TEST_DIR = 'tests_tables'

    def setUp(self) -> None:
        if not os.path.exists(self.TEST_DIR):
            os.mkdir(self.TEST_DIR)

        queries = [
            "create table foobar (primary key uid, a, b);",
            "insert into foobar set uid=1, a='a', b=100;",
            "insert into foobar set uid=2, a='b', b=100;",
            "insert into foobar set uid=3, a='c', b=200;",
            "insert into foobar set uid=4, a='d', b=200;",
            "insert into foobar set uid=5, a='e', b=300;",
            "insert into foobar set uid=6, a='f', b=300;",
        ]

        sql = "".join(queries)
        inter = Interpreter(tree=Parser(lex=Lexer(sql)).parse(), working_dir=self.TEST_DIR)
        inter.do()

    def tearDown(self) -> None:
        for filename in os.listdir(self.TEST_DIR):
            os.remove(os.path.join(self.TEST_DIR, filename))
        os.rmdir(self.TEST_DIR)

    @cases([
        ("select uid from foobar;", [[1], [2], [3], [4], [5], [6]]),
        ("select a from foobar;", [['a'], ['b'], ['c'], ['d'], ['e'], ['f']]),

        ("select uid, a from foobar;", [[1, 'a'], [2, 'b'], [3, 'c'], [4, 'd'], [5, 'e'], [6, 'f']]),
        ("select a, uid from foobar;", [['a', 1], ['b', 2], ['c', 3], ['d', 4], ['e', 5], ['f', 6]]),
        ("select a, a from foobar;", [['a', 'a'], ['b', 'b'], ['c', 'c'], ['d', 'd'], ['e', 'e'], ['f', 'f']]),

        ("select uid from foobar limit 1;", [[1]]),
        ("select uid from foobar limit 100500;", [[1], [2], [3], [4], [5], [6]]),

        ("select uid from foobar where uid=1;", [[1]]),
        ("select uid from foobar where uid=1 and uid=2;", [[2]]),
        ("select uid from foobar where uid=100500;", []),
        ("select uid from foobar where a='a';", [[1]]),
        ("select uid from foobar where uid=1 and a='a';", [[1]]),
        ("select uid from foobar where b=100;", [[1], [2]]),

        # select primary key order by primary key
        ("select uid from foobar order by uid asc limit 3;", [[1], [2], [3]]),
        ("select uid from foobar order by uid desc limit 3;", [[6], [5], [4]]),

        # select column order by primary key
        ("select a from foobar order by uid asc limit 3;", [['a'], ['b'], ['c']]),
        ("select a from foobar order by uid desc limit 3;", [['f'], ['e'], ['d']]),

        # select column order by column
        ("select a from foobar order by a asc limit 1;", [['a']]),
        ("select a from foobar order by a desc limit 1;", [['f']]),

        # select primary key order by column
        ("select uid from foobar order by a asc limit 1;", [[1]]),
        ("select uid from foobar order by a desc limit 1;", [[6]]),
    ])
    def test_select(self, sql, expected):
        inter = Interpreter(tree=Parser(lex=Lexer(sql)).parse(), working_dir=self.TEST_DIR)
        results = inter.do()
        self.assertEqual(expected, results[0])
