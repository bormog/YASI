from pprint import pprint
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

import pandas as pd

if __name__ == '__main__':
    # bool expr https://gist.github.com/leehsueh/1290686/36b0baa053072c377ac7fc801d53200d17039674

    text = "create table foo (primary key uid, a, b);"
    text += "insert into foo set uid=3, a='Hello', b=100;"
    text += "select uid, a, b from foo;"

    inter = Interpreter(tree=Parser(lex=Lexer(text)).parse(), working_dir='tables')
    output = inter.do()
    pprint(output)
