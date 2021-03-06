import lexer
import nodes
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

    def expr(self) -> nodes.Node:
        """
        expr -> term ((PLUS | MINUS) term)*
        """

        node = self.term()
        while self.token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.token.type == TokenType.PLUS:
                self.move_forward(TokenType.PLUS)
                node = nodes.BinaryOperation(left=node, token_type=TokenType.PLUS, right=self.term())
            elif self.token.type == TokenType.MINUS:
                self.move_forward(TokenType.MINUS)
                node = nodes.BinaryOperation(left=node, token_type=TokenType.MINUS, right=self.term())
        return node

    def term(self) -> nodes.Node:
        """
        term -> factor ((MUL | DIV) factor)*
        """

        node = self.factor()
        while self.token.type in (TokenType.MUL, TokenType.DIV):
            if self.token.type == TokenType.MUL:
                self.move_forward(TokenType.MUL)
                node = nodes.BinaryOperation(left=node, token_type=TokenType.MUL, right=self.factor())
            elif self.token.type == TokenType.DIV:
                self.move_forward(TokenType.DIV)
                node = nodes.BinaryOperation(left=node, token_type=TokenType.DIV, right=self.factor())
        return node

    def factor(self) -> nodes.Node:
        """
        factor -> INT | LPAREN expr RPAREN
        """

        if self.token.type == TokenType.INT:
            node = nodes.Number(self.token)
            self.move_forward(TokenType.INT)
        elif self.token.type == TokenType.LPAREN:
            self.move_forward(TokenType.LPAREN)
            node = self.expr()
            self.move_forward(TokenType.RPAREN)
        else:
            raise ParserUnexpectedToken(self.token, '%s | %s' % (TokenType.INT, TokenType.LPAREN))

        return node

    def create_stmt(self) -> nodes.Node:
        """
        create_stmt -> CREATE TABLE ID LPAREN PRIMARY KEY ID (COMMA ID)* RPAREN SEMICOLON
        Example: create table foobar ( primary key foo, bar, buz ) ;
        """

        self.move_forward(TokenType.CREATE)
        self.move_forward(TokenType.TABLE)

        table = nodes.Table(self.token)
        self.move_forward(TokenType.ID)

        self.move_forward(TokenType.LPAREN)
        self.move_forward(TokenType.PRIMARY)
        self.move_forward(TokenType.KEY)

        primary_key = nodes.Column(self.token)
        self.move_forward(TokenType.ID)

        columns = []
        while self.token.type == TokenType.COMMA:
            self.move_forward(TokenType.COMMA)
            column = nodes.Column(self.token)
            self.move_forward(TokenType.ID)
            columns.append(column)

        self.move_forward(TokenType.RPAREN)
        self.move_forward(TokenType.SEMICOLON)

        return nodes.CreateStatement(table, primary_key, columns)

    def describe_stmt(self) -> nodes.Node:
        """
        describe_stmt -> DESCRIBE ID SEMICOLON
        Example: describe foobar;
        """

        self.move_forward(TokenType.DESCRIBE)
        table = nodes.Table(self.token)
        self.move_forward(TokenType.ID)
        self.move_forward(TokenType.SEMICOLON)
        return nodes.DescribeStatement(table=table)

    def assignee_sub_stmt(self) -> nodes.Node:
        """
        assignee_sub_stmt -> ID EQUALS value
        Example: foo=5
        Example: foo='bar'
        """
        column = nodes.Column(self.token)
        self.move_forward(TokenType.ID)
        self.move_forward(TokenType.EQUALS)
        value = self.value()
        return nodes.Assign(left=column, right=value)

    def insert_stmt(self) -> nodes.Node:
        """
        insert_stmt -> INSERT INTO ID SET assignee_sub_stmt (assignee_sub_stmt)* SEMICOLON
        Example: insert into foobar set foo=4, bar='bar', buz=100500;
        """

        self.move_forward(TokenType.INSERT)
        self.move_forward(TokenType.INTO)

        table = nodes.Table(self.token)
        self.move_forward(TokenType.ID)

        assignments = []

        self.move_forward(TokenType.SET)

        assignments.append(self.assignee_sub_stmt())

        while self.token.type == TokenType.COMMA:
            self.move_forward(TokenType.COMMA)
            assignments.append(self.assignee_sub_stmt())

        self.move_forward(TokenType.SEMICOLON)

        return nodes.InsertStatement(table=table, assignments=assignments)

    def value(self) -> nodes.Node:
        """
        value -> INT | STRING
        Example: 100500
        Example 'foobar'
        """

        if self.token.type == TokenType.INT:
            node = nodes.Number(self.token)
            self.move_forward(TokenType.INT)
        elif self.token.type == TokenType.STRING:
            node = nodes.String(self.token)
            self.move_forward(TokenType.STRING)
        else:
            raise ParserUnexpectedToken(self.token, "%s or %s" % (TokenType.INT, TokenType.STRING))
        return node

    def select_stmt(self) -> nodes.Node:
        """
        select_stmt -> SELECT select_expr SEMICOLON
        """

        self.move_forward(TokenType.SELECT)
        result = self.select_expr()
        self.move_forward(TokenType.SEMICOLON)
        return result

    def select_expr(self) -> nodes.Node:
        """
        select_expr -> expr | ID (COMMA ID)* FROM ID (WHERE assignee_sub_stmt (AND assignee_sub_stmt)* (order_sub_stmt)? (limit_sub_stmt)?)?
        Example: select 1+1
        Example: select foo from foobar
        Example: select foo, bar from foobar where foo='foo', bar=100500
        """

        if self.token.type == TokenType.ID:
            result = []

            column = nodes.Column(self.token)
            self.move_forward(TokenType.ID)
            result.append(column)
            while self.token.type == TokenType.COMMA:
                self.move_forward(TokenType.COMMA)
                column = nodes.Column(self.token)
                self.move_forward(TokenType.ID)
                result.append(column)

            self.move_forward(TokenType.FROM)
            table = nodes.Table(self.token)
            self.move_forward(TokenType.ID)

            where = []
            if self.token.type == TokenType.WHERE:
                self.move_forward(TokenType.WHERE)
                where.append(self.assignee_sub_stmt())

                while self.token.type == TokenType.AND:
                    self.move_forward(TokenType.AND)
                    where.append(self.assignee_sub_stmt())

            if self.token.type == TokenType.ORDER:
                order = self.order_sub_stmt()
            else:
                order = nodes.Empty()

            if self.token.type == TokenType.LIMIT:
                limit = self.limit_sub_stmt()
            else:
                limit = nodes.Empty()

            node = nodes.SelectStatement(
                table=table,
                result=result,
                where=where,
                order=order,
                limit=limit
            )
        else:
            node = nodes.SelectStatement(
                table=nodes.Empty(),
                result=self.expr(),
                where=None,
                order=nodes.Empty(),
                limit=nodes.Empty()
            )
        return node

    def order_sub_stmt(self) -> nodes.Node:
        """
        order_sub_stmt -> ORDER BY ID (ASC | DESC)
        Example: order by foo asc
        """

        self.move_forward(TokenType.ORDER)
        self.move_forward(TokenType.BY)

        by = nodes.Column(self.token)
        self.move_forward(TokenType.ID)

        asc_desc = self.token.type
        if self.token.type == TokenType.ASC:
            self.move_forward(TokenType.ASC)
        elif self.token.type == TokenType.DESC:
            self.move_forward(TokenType.DESC)
        else:
            raise ParserUnexpectedToken(self.token, "%s | %s" % (TokenType.ASC, TokenType.DESC))
        return nodes.Order(by, asc_desc)

    def limit_sub_stmt(self) -> nodes.Node:
        """
        limit_sub_stmt -> LIMIT NUMBER
        Example: limit 10
        """

        self.move_forward(TokenType.LIMIT)
        limit = nodes.Number(self.token)
        self.move_forward(TokenType.INT)
        return limit

    def stmt(self) -> nodes.Node:
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

    def stmt_list(self) -> nodes.Statements:
        """
        stmt_list -> stmt (stmt)*
        """
        result = []
        while self.token.type != TokenType.EOF:
            res = self.stmt()
            result.append(res)
        return nodes.Statements(result)

    def parse(self) -> nodes.Statements:
        return self.stmt_list()
