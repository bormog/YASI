import os
from flask import Flask, render_template, request, flash

from interpreter import Interpreter
from lexer import Lexer, LexerException
from parser import Parser, ParserException
from storage import TableNotExists, TableColumnNotExists, StorageException

from web.demo import initialize

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


def startapp():
    working_dir = os.getenv("WORKING_DIR")
    initialize(working_dir)


app.before_first_request(startapp)


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
        content = "select uid, name, num_of_jobs, avg_salary from languages;"

    return render_template('index.html', content=content, results=results, error=error)
