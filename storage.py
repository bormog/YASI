import io
import os
from typing import Union

import pandas as pd


class StorageException(Exception):
    pass


class TableNotExists(StorageException):

    def __init__(self, name):
        msg = "Table %s not exists" % name
        super().__init__(msg)


class TableColumnNotExists(StorageException):

    def __init__(self, name, column):
        msg = "Column %s not exists in table %s" % (column, name)
        super().__init__(msg)


class Table:

    def __init__(self, primary_key=None, columns=None):
        if primary_key is not None and columns is not None:
            self.primary_key = primary_key
            self.columns = columns
            df = pd.DataFrame(columns=[primary_key] + columns)
            self.df = df.set_index(primary_key)
        else:
            self.primary_key = None
            self.columns = []
            self.df = None

    @staticmethod
    def load(filepath: Union[str, io.StringIO]) -> 'Table':
        table = Table()
        table.df = pd.read_csv(filepath, index_col=0)
        table.primary_key = table.df.index.name
        table.columns = table.df.columns.to_list()
        return table

    def column_exists(self, name: str) -> bool:
        return name == self.primary_key or name in self.columns

    def save(self, filepath: Union[str, io.StringIO]) -> None:
        self.df.to_csv(filepath, index_label=self.df.index.name)

    def info(self) -> list:
        return [self.primary_key] + self.columns

    def insert(self, data: dict) -> None:
        row = pd.DataFrame(data, columns=[self.primary_key] + self.columns)
        row = row.set_index(self.df.index.name)
        self.df = pd.concat([self.df, row])

    def select(self, result: list, where: list, order: tuple = None, limit: int = 0) -> list:
        search = self.df

        pk = None
        conditions = []
        for name, value in where:
            if name == self.primary_key:
                pk = value
            else:
                conditions.append((name, value,))

        if pk is not None:
            try:
                search = search.loc[[pk], :]
            except KeyError:
                return []

        for name, value in conditions:
            search = search[search[name] == value]

        if self.primary_key in result:
            search = search.reset_index()

        if order:
            column, ascending = order
            search = search.sort_values(by=column, ascending=ascending)

        search = search[result]

        if limit:
            search = search[:limit]
        return search.values.tolist()


class Storage:

    def __init__(self, working_dir: str):
        if not os.path.exists(working_dir):
            raise StorageException("%s working dir is not exists")
        self._working_dir = working_dir

    def _path(self, name: str) -> str:
        filename = "%s.csv" % name
        return os.path.join(self._working_dir, filename)

    def _exists(self, name: str) -> bool:
        return os.path.exists(self._path(name))

    def create(self, name: str, primary: str, columns: list) -> bool:
        if self._exists(name):
            return False
        Table(primary, columns).save(self._path(name))
        return self._exists(name)

    def describe(self, name: str) -> list:
        if not self._exists(name):
            raise TableNotExists(name)
        return Table.load(self._path(name)).info()

    def insert(self, name: str, columns: list) -> None:
        if not self._exists(name):
            raise TableNotExists(name)
        table = Table.load(self._path(name))
        row = {}
        for column, value in columns:
            if not table.column_exists(column):
                raise TableColumnNotExists(name, column)
            else:
                row[column] = [value]

        if table.primary_key not in row.keys():
            raise StorageException("Primary key %s is required" % table.primary_key)
        if not row[table.primary_key][0]:
            raise StorageException("Primary key cant by empty")
        if row[table.primary_key][0] in table.df.index.values:
            raise StorageException("Such primary key %s already exists" % row[table.primary_key][0])

        table.insert(row)
        table.save(self._path(name))

    def select(self, name: str, result: list, where: list, order: tuple = None, limit: int = None) -> list:
        if not self._exists(name):
            raise TableNotExists(name)
        table = Table.load(self._path(name))
        for column in result:
            if not table.column_exists(column):
                raise TableColumnNotExists(name, column)
        for column, _ in where:
            if not table.column_exists(column):
                raise TableColumnNotExists(name, column)
        if order:
            column, ascending = order
            if not table.column_exists(column):
                raise TableColumnNotExists(name, column)
        return table.select(result, where, order, limit)
