from flask import Flask, render_template, request, flash

from interpreter import Interpreter
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from storage import TableNotExists, TableColumnNotExists, StorageException

app = Flask(__name__)
app.config["SECRET_KEY"] = "foobar"

"""
todo
 - 2 templates: base and index
 - left - textarea, right - how to + rules
 - errors -  red flash
 - results -  nice list
 
 - secret key from env
 - create file with demo data if not exists
 - initial query in textarea
"""


@app.route("/",  methods=("GET", "POST"))
def index():
    content = ""
    results = []
    error = None

    if request.method == "POST":
        content = request.form["content"]
        if not content:
            flash("Please provide SQL query")
        else:
            try:
                inter = Interpreter(tree=Parser(lex=Lexer(content)).parse(), working_dir="tables")
                results = inter.do()
            except LexerException as err:
                error = "Lexer Error: %s" % str(err)
            except ParserException as err:
                error = "Parser Error: %s" % str(err)
            except (TableNotExists, TableColumnNotExists, StorageException) as err:
                error = "Storage Error: %s" % str(err)
            except Exception as err:
                error = "Error: %s" % str(err)
    elif request.method == "GET":
        content = "describe foo;"

    return render_template('index.html', content=content, results=results, error=error)
