import re

import ast
from tokens import TokenType

UNDERSCORE_RE = re.compile(r'(?<!^)(?=[A-Z])')


def get_visit_method_name(node):
    if not isinstance(node, ast.Node):
        raise Exception("Must be instance of ast.Node")
    name = type(node).__name__
    return "visit_%s" % UNDERSCORE_RE.sub('_', name).lower()


class NodeVisitor:

    def visit(self, node):
        method_name = get_visit_method_name(node)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError("Method = %s for node %s not implemented" % (get_visit_method_name(node), node))


class Interpreter(NodeVisitor):

    def __init__(self, tree):
        self.tree = tree

    def visit_statements(self, node):
        results = []
        for child in node.children:
            results.append(self.visit(child))
        return results

    def visit_number(self, node):
        return int(node.value)

    def visit_string(self, node):
        return str(node.value)

    def visit_table(self, node):
        return node.name

    def visit_column(self, node):
        return node.name

    def visit_binary_operation(self, node):
        if node.operation == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operation == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operation == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operation == TokenType.DIV:
            return self.visit(node.left) // self.visit(node.right)
        else:
            raise Exception('Unknown operation %s' % node.operation)

    def visit_assign(self, node):
        var = self.visit(node.left)
        value = self.visit(node.right)
        return var, value

    def visit_create_statement(self, node):
        table = self.visit(node.table)
        primary_key = self.visit(node.primary_key)
        columns = [self.visit(column) for column in node.columns]
        return "create table = %s, key = %s, columns = %s" % (
            table, primary_key, columns)

    def visit_describe_statement(self, node):
        table = self.visit(node.table)
        return "describe table = %s" % table

    def visit_insert_statement(self, node):
        table = self.visit(node.table)
        assignments = [self.visit(asignee) for asignee in node.assignments]
        return "insert into table %s, columns = %s" % (table, assignments)

    def visit_select_statement(self, node):
        print(node.result)
        if isinstance(node.result, ast.BinaryOperation):
            return self.visit(node.result)
        else:
            table = self.visit(node.table)
            result = [self.visit(column) for column in node.result]
            where = [self.visit(asignee) for asignee in node.where]
        return "select from %s, result = %s, where = %s" % (table, result, where)

    def do(self):
        if self.tree is not None:
            return self.visit(self.tree)
