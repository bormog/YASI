import io
import csv
import unittest

from tests.helpers import cases

from storage import Table


class BuffTable:

    def __init__(self):
        self.buff = io.StringIO()
        self.writer = csv.writer(self.buff, delimiter=',')

    def insert(self, header):
        self.writer.writerow(header)

    def save(self):
        self.buff.seek(0)


class TestTable(unittest.TestCase):

    def setUp(self) -> None:
        self.buff = io.StringIO

    def tearDown(self) -> None:
        self.buff = None

    def test_table_init(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])
        self.assertEqual("uid", table.primary_key)
        self.assertEqual(["col1", "col2", "col3"], table.columns)
        self.assertEqual("uid", table.df.index.name)

    def test_table_save(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])
        buff = io.StringIO()
        table.save(buff)
        buff.seek(0)

        reader = csv.reader(buff, delimiter=',')
        header = next(reader)
        self.assertEqual(["uid", "col1", "col2", "col3"], header)

    def test_table_load(self):
        header = ["uid", "col1", "col2", "col3"]
        row = [1, "col11", "col12", "col13"]
        buff_table = BuffTable()
        buff_table.insert(header)
        buff_table.insert(row)
        buff_table.save()

        table = Table.load(buff_table.buff)
        self.assertEqual("uid", table.primary_key)
        self.assertEqual(["col1", "col2", "col3"], table.columns)
        self.assertEqual([['col11', 'col12', 'col13']], table.df.values.tolist())

    def test_table_column_exists(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])

        self.assertEqual(True, table.column_exists("uid"))
        self.assertEqual(True, table.column_exists("col1"))
        self.assertEqual(False, table.column_exists("foo"))

    def test_table_info(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])
        self.assertEqual(["uid", "col1", "col2", "col3"], table.info())

    def test_table_insert(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])
        table.insert(dict(uid=[1], col1=["col11"], col2=["col12"], col3=["col13"]))
        self.assertEqual([1], table.df.index.values)
        self.assertEqual([['col11', 'col12', 'col13']], table.df.values.tolist())

    @cases([
        (
                # select uid
                (["uid"], [], 0),
                ([[1], [2], [3]])
        ),
        (
                # select foo
                (["foo"], [], 0),
                ([["a"], ["b"], ["c"]])

        ),
        (
                # select uid, foo
                (["uid", "foo"], [], 0),
                ([[1, "a"], [2, "b"], [3, "c"]])
        ),
        (
                # select foo, uid
                (["foo", "uid"], [], 0),
                ([["a", 1], ["b", 2], ["c", 3]])
        ),
        (
                # select uid limit 1
                (["uid"], [], 1),
                ([[1]])
        ),
        (
                # select uid limit 100
                (["uid"], [], 100),
                ([[1], [2], [3]])
        ),
        (
                # select uid where uid = 2
                (["uid"], [("uid", 2)], 0),
                ([[2]])
        ),
        (
                # select uid where uid = 100500
                (["uid"], [("uid", 100500)], 0),
                ([])
        ),
        (
                # select uid where foo=c
                (["uid"], [("foo", "c")], 0),
                ([[3]])
        ),
        (
                # select uid where uid=3 and foo=c
                (["uid"], [("uid", 3), ("foo", "c")], 0),
                ([[3]])
        ),

    ])
    def test_table_select(self, query, expected):
        header = ["uid", "foo", "bar"]
        rows = [
            [1, "a", 100],
            [2, "b", 200],
            [3, "c", 300],
        ]
        buff_table = BuffTable()
        buff_table.insert(header)
        for row in rows:
            buff_table.insert(row)
        buff_table.save()

        table = Table.load(buff_table.buff)
        values = table.select(*query)
        self.assertEqual(expected, values)
