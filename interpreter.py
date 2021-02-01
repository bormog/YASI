import re

import nodes
from storage import Storage
from tokens import TokenType

UNDERSCORE_RE = re.compile(r'(?<!^)(?=[A-Z])')


def get_visit_method_name(node: nodes.Node) -> str:
    if not isinstance(node, nodes.Node):
        raise Exception("Must be instance of ast.Node")
    name = type(node).__name__
    return "visit_%s" % UNDERSCORE_RE.sub('_', name).lower()


class NodeVisitor:

    def visit(self, node: nodes.Node) -> any:
        method_name = get_visit_method_name(node)
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: nodes.Node):
        raise NotImplementedError("Method = %s for node %s not implemented" % (get_visit_method_name(node), node))


class Interpreter(NodeVisitor):

    def __init__(self, tree: nodes.Node, working_dir: str) -> None:
        self.tree = tree
        self.storage = Storage(working_dir)

    def visit_statements(self, node: nodes.Statements) -> list:
        results = []
        for child in node.children:
            results.append(self.visit(child))
        return results

    def visit_number(self, node: nodes.Number) -> int:
        return int(node.value)

    def visit_string(self, node: nodes.String) -> str:
        return str(node.value.strip("'"))

    def visit_table(self, node: nodes.Table) -> str:
        return node.name

    def visit_column(self, node: nodes.Column) -> str:
        return node.name

    def visit_binary_operation(self, node: nodes.BinaryOperation) -> int:
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

    def visit_assign(self, node: nodes.Assign) -> tuple:
        var = self.visit(node.left)
        value = self.visit(node.right)
        return var, value

    def visit_create_statement(self, node: nodes.CreateStatement) -> bool:
        table = self.visit(node.table)
        primary_key = self.visit(node.primary_key)
        columns = [self.visit(column) for column in node.columns]
        return self.storage.create(table, primary_key, columns)

    def visit_describe_statement(self, node: nodes.DescribeStatement) -> list:
        table = self.visit(node.table)
        return self.storage.describe(table)

    def visit_insert_statement(self, node: nodes.InsertStatement) -> None:
        table = self.visit(node.table)
        assignments = [self.visit(asignee) for asignee in node.assignments]
        return self.storage.insert(table, assignments)

    def visit_select_statement(self, node: nodes.SelectStatement) -> list:
        if isinstance(node.result, nodes.BinaryOperation):
            return self.visit(node.result)
        else:
            table = self.visit(node.table)
            result = [self.visit(column) for column in node.result]
            where = [self.visit(asignee) for asignee in node.where]
            limit = self.visit(node.limit)
            return self.storage.select(table, result, where, limit)

    def do(self):
        if self.tree is not None:
            return self.visit(self.tree)
