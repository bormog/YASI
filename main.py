from pprint import pprint

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser

import pandas as pd

if __name__ == '__main__':
    text = "create table foobar (primary key foo, bar, buz, foobar);"
    text += "describe foobar;"
    # text += "insert into foobar set foo='foo', bar=2, buz=4, foobar=5;"
    text += "select 99 + 1;"
    text += "select bar, foo, buz from foobar where foo=12 limit 3;"

    lex = Lexer(text)
    parser = Parser(lex)
    tree = parser.parse()

    inter = Interpreter(tree)
    output = inter.do()
    pprint(output)
    # df = pd.DataFrame({'name': ['Raphael', 'Donatello', 'Raphael'],
    #                    'mask': ['red', 'purple', 'green'],
    #                    'weapon': ['sai', 'bo staff', 'ok']})
    # # df = df.set_index('name')
    #
    # s = df
    # # s = s.loc['Raphael']
    # # s = s.reset_index()
    # s = s[s["mask"] == "red"][["mask", "name", "weapon"]]
    # print(s.index.values)
    # print(s.values.tolist())
    # df.to_csv('foo.csv', index_label=df.index.name)

