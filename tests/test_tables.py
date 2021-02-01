import io
import csv
import unittest

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
        # todo check values
        header = ["uid", "col1", "col2", "col3"]
        buff_table = BuffTable()
        buff_table.insert(header)
        buff_table.save()

        table = Table.load(buff_table.buff)
        self.assertEqual("uid", table.primary_key)
        self.assertEqual(["col1", "col2", "col3"], table.columns)

    def test_table_column_exists(self):
        header = ["uid", "col1", "col2", "col3"]
        buff_table = BuffTable()
        buff_table.insert(header)
        buff_table.save()

        table = Table.load(buff_table.buff)
        self.assertEqual(True, table.column_exists("uid"))
        self.assertEqual(True, table.column_exists("col1"))
        self.assertEqual(False, table.column_exists("foo"))

    def test_table_info(self):
        header = ["uid", "col1", "col2", "col3"]
        buff_table = BuffTable()
        buff_table.insert(header)
        buff_table.save()

        table = Table.load(buff_table.buff)
        self.assertEqual(header, table.info())

    def test_table_insert(self):
        table = Table(primary_key="uid", columns=["col1", "col2", "col3"])
        table.insert(dict(uid=[1], col1=["col11"], col2=["col12"], col3=["col13"]))
        self.assertEqual([1], table.df.index.values)
        self.assertEqual([['col11', 'col12', 'col13']], table.df.values.tolist())

    def test_table_select(self):
        pass



