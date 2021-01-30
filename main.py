from pprint import pprint

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser

if __name__ == '__main__':
    text = "create table foobar (primary key foo, bar, buz, foobar);"
    text += "describe foobar;"
    # text += "insert into foobar set foo='foo', bar=2, buz=4, foobar=5;"
    text += "select 1 + 1 + 2 * 2 + 3 * (1 - 1);"
    text += "select foo, bar from foobar where foo='foo', bar=2;"

    lex = Lexer(text)
    parser = Parser(lex)
    tree = parser.parse()

    inter = Interpreter(tree)
    output = inter.do()
    pprint(output)

