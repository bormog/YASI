import os
import pandas as pd


class StorageException(Exception):
    pass


class Storage:

    def __init__(self, working_dir: str = "tables"):
        if not os.path.exists(working_dir):
            raise StorageException("%s working dir is not exists")
        self._working_dir = working_dir
        self._tables = {}

    def _name(self, table: str) -> str:
        return "%s.csv" % table

    def _path(self, table: str) -> str:
        return os.path.join(self._working_dir, self._name(table))

    def _exists(self, table: str) -> bool:
        path = self._path(table)
        return os.path.exists(path)

    def _load(self, table: str) -> pd.DataFrame:
        if not self._exists(table):
            raise StorageException("This table %s is not exists" % table)
        df = pd.read_csv(self._path(table))
        return self._set(table, df)

    def _set(self, table: str, df: pd.DataFrame) -> pd.DataFrame:
        self._tables[table] = df
        return self._get(table)

    def _get(self, table: str) -> pd.DataFrame:
        return self._tables[table]

    def _save(self, table: str) -> None:
        self._get(table).to_csv(self._path(table), index=False)

    def _column_exists(self, table: str, column: str) -> bool:
        columns = self._get(table).columns.to_list()
        for c in columns:
            if c == column:
                return True
        return False

    def create(self, table: str, primary: str, columns: list) -> bool:
        if self._exists(table):
            return False
        _columns = [primary] + columns
        df = pd.DataFrame(columns=_columns)
        self._set(table, df).to_csv(self._path(table), index=False)
        return self._exists(table)

    def describe(self, table: str) -> list:
        self._load(table)
        return self._get(table).columns.to_list()

    def insert(self, table: str, columns: list) -> None:
        self._load(table)

        row = {}
        for column, value in columns:
            if not self._column_exists(table, column):
                raise StorageException("Column %s not exists in table %s" % (column, table))
            else:
                row[column] = value

        df = self._get(table).append(row, ignore_index=True)
        self._set(table, df)
        self._save(table)

    def select(self, table: str, result: list, where: list, limit: int = None) -> list:
        self._load(table)
        df = self._get(table)

        for column in result:
            if not self._column_exists(table, column):
                raise StorageException("Column %s not exists in table %s" % (column, table))

        conditions = None
        for column, value in where:
            if not self._column_exists(table, column):
                raise StorageException("Column %s not exists in table %s" % (column, table))
            condition = (df[column] == value)
            if conditions is None:
                conditions = condition
            else:
                conditions = condition & condition
        search = df[conditions][result]
        if limit:
            search = search[:limit]
        return search.values.tolist()


