from tokens import Token


class Node:
    pass


class Empty(Node):
    pass


class Number(Node):

    def __init__(self, token: Token):
        self.token = token
        self.value = token.value


class String(Node):

    def __init__(self, token: Token):
        self.token = token
        self.value = token.value


class Identifier(Node):

    def __init__(self, token: Token):
        self.token = token
        self.name = token.value


class Table(Identifier):
    pass


class Column(Identifier):
    pass


class Order(Node):

    def __init__(self, column: Column, order):
        self.column = column
        self.order = order


class Assign(Node):

    def __init__(self, left: Column, right: any):
        self.left = left
        self.right = right


class BinaryOperation(Node):

    def __init__(self, left, token_type, right):
        self.left = left
        self.right = right
        self.operation = token_type


class DescribeStatement(Node):

    def __init__(self, table):
        self.table = table


class Statements(Node):

    def __init__(self, children):
        self.children = children


class CreateStatement(Node):

    def __init__(self, table, primary_key, columns):
        self.table = table
        self.primary_key = primary_key
        self.columns = columns


class InsertStatement(Node):

    def __init__(self, table, assignments):
        self.table = table
        self.assignments = assignments


class SelectStatement(Node):

    def __init__(self, table, result, where, order, limit=0):
        self.table = table
        self.result = result
        self.where = where
        self.order = order
        self.limit = limit
