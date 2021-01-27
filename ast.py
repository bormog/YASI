class Node:
    pass


class Number(Node):

    def __init__(self, token):
        self.token = token
        self.value = token.value


class String(Node):

    def __init__(self, token):
        self.token = token
        self.value = token.value


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

    def __init__(self, table, columns):
        self.table = table
        self.columns = columns


class SelectStatement(Node):

    def __init__(self, table, result, where):
        self.table = table
        self.result = result
        self.where = where
