import ast
import lexer
from tokens import TokenType, Token


class ParserException(Exception):
    pass


class ParserUnexpectedToken(ParserException):

    def __init__(self, token: Token, expected: any):
        msg = "Unexpected token %s, at pos %d. Required %s" % (token.value, token.pos, repr(expected))
        super().__init__(msg)


class Parser:

    def __init__(self, lex: lexer.Lexer):
        self.lexer = iter(lex)
        self.token = self.get_next_token()

    def get_next_token(self) -> Token:
        return next(self.lexer)

    def move_forward(self, token_type: TokenType) -> None:
        if self.token.type == token_type:
            self.token = self.get_next_token()
        else:
            raise ParserUnexpectedToken(self.token, token_type)

    def expr(self) -> ast.Node:
        """
        expr -> term ((PLUS | MINUS) term)*
        """

        node = self.term()
        while self.token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.token.type == TokenType.PLUS:
                self.move_forward(TokenType.PLUS)
                node = ast.BinaryOperation(left=node, token_type=TokenType.PLUS, right=self.term())
            elif self.token.type == TokenType.MINUS:
                self.move_forward(TokenType.MINUS)
                node = ast.BinaryOperation(left=node, token_type=TokenType.MINUS, right=self.term())
        return node

    def term(self) -> ast.Node:
        """
        term -> factor ((MUL | DIV) factor)*
        """

        node = self.factor()
        while self.token.type in (TokenType.MUL, TokenType.DIV):
            if self.token.type == TokenType.MUL:
                self.move_forward(TokenType.MUL)
                node = ast.BinaryOperation(left=node, token_type=TokenType.MUL, right=self.factor())
            elif self.token.type == TokenType.DIV:
                self.move_forward(TokenType.DIV)
                node = ast.BinaryOperation(left=node, token_type=TokenType.DIV, right=self.factor())
        return node

    def factor(self) -> ast.Node:
        """
        factor -> INT | LPAREN expr RPAREN
        """

        if self.token.type == TokenType.INT:
            node = ast.Number(self.token)
            self.move_forward(TokenType.INT)
        elif self.token.type == TokenType.LPAREN:
            self.move_forward(TokenType.LPAREN)
            node = self.expr()
            self.move_forward(TokenType.RPAREN)
        else:
            raise ParserUnexpectedToken(self.token, '%s | %s' % (TokenType.INT, TokenType.LPAREN))

        return node

    def create_stmt(self) -> ast.Node:
        """
        create_stmt -> CREATE TABLE ID LPAREN PRIMARY KEY ID (COMMA ID)* RPAREN SEMICOLON
        Example: create table foobar ( primary key foo, bar, buz ) ;
        """

        self.move_forward(TokenType.CREATE)
        self.move_forward(TokenType.TABLE)

        table = ast.Table(self.token)
        self.move_forward(TokenType.ID)

        self.move_forward(TokenType.LPAREN)
        self.move_forward(TokenType.PRIMARY)
        self.move_forward(TokenType.KEY)

        primary_key = ast.Column(self.token)
        self.move_forward(TokenType.ID)

        columns = []
        while self.token.type == TokenType.COMMA:
            self.move_forward(TokenType.COMMA)
            column = ast.Column(self.token)
            self.move_forward(TokenType.ID)
            columns.append(column)

        self.move_forward(TokenType.RPAREN)
        self.move_forward(TokenType.SEMICOLON)

        return ast.CreateStatement(table, primary_key, columns)

    def describe_stmt(self) -> ast.Node:
        """
        describe_stmt -> DESCRIBE ID SEMICOLON
        Example: describe foobar;
        """

        self.move_forward(TokenType.DESCRIBE)
        table = ast.Table(self.token)
        self.move_forward(TokenType.ID)
        self.move_forward(TokenType.SEMICOLON)
        return ast.DescribeStatement(table=table)

    def insert_stmt(self) -> ast.Node:
        """
        insert_stmt -> INSERT INTO ID SET ID EQUALS value (COMMA ID EQUALS value)* SEMICOLON
        Example: insert into foobar set foo=4, bar='bar', buz=100500;
        """

        self.move_forward(TokenType.INSERT)
        self.move_forward(TokenType.INTO)

        table = ast.Table(self.token)
        self.move_forward(TokenType.ID)

        assignments = []

        self.move_forward(TokenType.SET)
        column = ast.Column(self.token)
        self.move_forward(TokenType.ID)
        self.move_forward(TokenType.EQUALS)
        value = self.value()
        assignments.append(ast.Assign(left=column, right=value))

        while self.token.type == TokenType.COMMA:
            self.move_forward(TokenType.COMMA)
            column = ast.Column(self.token)
            self.move_forward(TokenType.ID)
            self.move_forward(TokenType.EQUALS)
            value = self.value()
            assignments.append(ast.Assign(left=column, right=value))

        self.move_forward(TokenType.SEMICOLON)

        return ast.InsertStatement(table=table, assignments=assignments)

    def value(self) -> ast.Node:
        """
        value -> INT | STRING
        Example: 100500
        Example 'foobar'
        """

        if self.token.type == TokenType.INT:
            node = ast.Number(self.token)
            self.move_forward(TokenType.INT)
        elif self.token.type == TokenType.STRING:
            node = ast.String(self.token)
            self.move_forward(TokenType.STRING)
        else:
            raise ParserUnexpectedToken(self.token, "%s or %s" % (TokenType.INT, TokenType.STRING))
        return node

    def select_stmt(self) -> ast.Node:
        """
        select_stmt -> SELECT select_expr SEMICOLON
        """

        self.move_forward(TokenType.SELECT)
        result = self.select_expr()
        self.move_forward(TokenType.SEMICOLON)
        return result

    def select_expr(self) -> ast.Node:
        """
        select_expr -> expr | ID (COMMA ID)* FROM ID ( WHERE ID EQUALS variable (COMMA ID EQUALS variable)* )*
        Example: select 1+1
        Example: select foo from foobar
        Example: select foo, bar from foobar where foo='foo', bar=100500
        """

        if self.token.type == TokenType.ID:
            result = []

            column = ast.Column(self.token)
            self.move_forward(TokenType.ID)
            result.append(column)
            while self.token.type == TokenType.COMMA:
                self.move_forward(TokenType.COMMA)
                column = ast.Column(self.token)
                self.move_forward(TokenType.ID)
                result.append(column)

            self.move_forward(TokenType.FROM)
            table = ast.Table(self.token)
            self.move_forward(TokenType.ID)

            where = []
            if self.token.type == TokenType.WHERE:
                self.move_forward(TokenType.WHERE)
                column = ast.Column(self.token)
                self.move_forward(TokenType.ID)
                self.move_forward(TokenType.EQUALS)
                value = self.value()
                where.append(ast.Assign(left=column, right=value))

                while self.token.type == TokenType.COMMA:
                    self.move_forward(TokenType.COMMA)
                    column = ast.Column(self.token)
                    self.move_forward(TokenType.ID)
                    self.move_forward(TokenType.EQUALS)
                    value = self.value()
                    where.append(ast.Assign(left=column, right=value))
            node = ast.SelectStatement(table=table, result=result, where=where)
        else:
            node = ast.SelectStatement(table=None, result=self.expr(), where=None)
        return node

    def stmt(self) -> ast.Node:
        """
        stmt -> create_stmt | describe_stmt | insert_stmt | select_stmt
        """

        if self.token.type == TokenType.CREATE:
            result = self.create_stmt()
        elif self.token.type == TokenType.DESCRIBE:
            result = self.describe_stmt()
        elif self.token.type == TokenType.INSERT:
            result = self.insert_stmt()
        elif self.token.type == TokenType.SELECT:
            result = self.select_stmt()
        else:
            raise ParserUnexpectedToken(self.token, "%s | %s | %s | %s" % (TokenType.CREATE, TokenType.DESCRIBE,
                                                                           TokenType.INSERT, TokenType.SELECT))

        return result

    def stmt_list(self) -> ast.Statements:
        """
        stmt_list -> stmt (stmt)*
        """
        result = []
        while self.token.type != TokenType.EOF:
            res = self.stmt()
            result.append(res)
        return ast.Statements(result)

    def parse(self) -> ast.Statements:
        return self.stmt_list()
