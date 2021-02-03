import os
import unittest

from storage import Storage, StorageException, TableNotExists, TableColumnNotExists
from tests.helpers import cases


class TestStorage(unittest.TestCase):
    TEST_DIR = 'tests_storage'

    def setUp(self) -> None:
        if not os.path.exists(self.TEST_DIR):
            os.mkdir(self.TEST_DIR)
        self.storage = Storage(self.TEST_DIR)

    def tearDown(self) -> None:
        for filename in os.listdir(self.TEST_DIR):
            os.remove(os.path.join(self.TEST_DIR, filename))
        os.rmdir(self.TEST_DIR)

    def test_init_raise_exception_on_invalid_dir(self):
        with self.assertRaises(StorageException):
            Storage("foobar")

    def test_create(self):
        name = "foobar"
        self.assertEqual(False, self.storage._exists(name))
        created = self.storage.create("foobar", "uid", [])
        self.assertEqual(True, created)
        self.assertEqual(True, self.storage._exists(name))

        created = self.storage.create("foobar", "uid", [])
        self.assertEqual(False, created)

    def test_describe_raise_exception_on_invalid_table(self):
        with self.assertRaises(TableNotExists):
            self.storage.describe("foobar")

    def test_insert_raise_exception_on_invalid_table(self):
        with self.assertRaises(TableNotExists):
            self.storage.insert("foobar", [("a", 1, )])

    def test_insert_raise_exception_on_invalid_columns(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        with self.assertRaises(TableColumnNotExists):
            self.storage.insert("foobar", [("a", 1, )])

    def test_insert_raise_exception_without_pk(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        with self.assertRaises(StorageException):
            self.storage.insert("foobar", [("foo", 1), ("bar", 1)])

    def test_insert_raise_exception_with_empty_pk(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        with self.assertRaises(StorageException):
            self.storage.insert("foobar", [("uid", ""), ("foo", 1), ("bar", 1)])

    def test_insert_raise_exception_with_duplicate_pk(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        self.storage.insert("foobar", [("uid", 1), ("foo", 1), ("bar", 1)])
        with self.assertRaises(StorageException):
            self.storage.insert("foobar", [("uid", 1), ("foo", 1), ("bar", 1)])

    def test_select_raise_exception_on_invalid_where(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        with self.assertRaises(TableColumnNotExists):
            self.storage.select("foobar", ["uid"], [("a", 1)])

    def test_select_raise_exception_on_invalid_result(self):
        self.storage.create("foobar", "uid", ["foo", "bar"])
        with self.assertRaises(TableColumnNotExists):
            self.storage.select("foobar", ["a"], [("foo", 1)])

    def test_select_raise_exception_on_invalid_table(self):
        with self.assertRaises(TableNotExists):
            self.storage.select("foobar", ["uid"], [])




