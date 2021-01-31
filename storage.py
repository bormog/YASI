import os

import pandas as pd


class StorageException(Exception):
    pass


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
    def load(filepath: str):
        table = Table()
        table.df = pd.read_csv(filepath, index_col=0)
        table.primary_key = table.df.index.name
        table.columns = table.df.columns.to_list()
        return table

    def column_exists(self, name: str) -> bool:
        return name == self.primary_key or name in self.columns

    def save(self, filepath: str) -> None:
        self.df.to_csv(filepath, index_label=self.df.index.name)

    def info(self) -> list:
        return self.columns

    def insert(self, data: dict) -> None:
        row = pd.DataFrame(data, columns=[self.primary_key] + self.columns)
        row = row.set_index(self.df.index.name)
        self.df = pd.concat([self.df, row])

    def select(self, result: list, where: list, limit: int = 0):
        search = self.df
        search = search.reset_index()

        conditions = None
        for column, value in where:
            filter = (search[column] == value)
            if conditions is None:
                conditions = filter
            else:
                conditions = conditions & filter

        if conditions is not None:
            search = search[conditions]

        search = search[result]

        if limit:
            search = search[:limit]
        return search.values.tolist()


class Storage:

    def __init__(self, working_dir: str = "tables"):
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
        return Table.load(self._path(name)).columns

    def insert(self, name: str, columns: list) -> None:
        table = Table.load(self._path(name))
        row = {}
        for column, value in columns:
            if not table.column_exists(column):
                raise StorageException("Column %s not exists in table %s" % (column, name))
            else:
                row[column] = [value]

        if table.primary_key not in row.keys():
            raise StorageException("Primary key %s is required" % table.primary_key)
        if row[table.primary_key][0] in table.df.index.values:
            raise StorageException("Such primary key %s already exists" % row[table.primary_key][0])

        table.insert(row)
        table.save(self._path(name))

    def select(self, name: str, result: list, where: list, limit: int = None) -> list:
        table = Table.load(self._path(name))
        for column in result:
            if not table.column_exists(column):
                raise StorageException("Column %s not exists in table %s" % (column, name))
        for column, _ in where:
            if not table.column_exists(column):
                raise StorageException("Column %s not exists in table %s" % (column, name))
        return table.select(result, where, limit)
