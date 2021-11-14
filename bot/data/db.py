import sqlite3
from typing import Optional

from bot.data.adapters import Adapter
from bot.data.store import KeyStore, Store
from bot.util.iterator import Iterator


class SqlExecutor(object):
    CREATE_TABLE_FORMAT = "CREATE TABLE IF NOT EXISTS {table} {columns}"

    def __init__(self, connection_string: str):
        self._connection = sqlite3.connect(connection_string)

    def create_table(self, name: str, columns_def: str):
        self.execute_update(self.CREATE_TABLE_FORMAT.format(table=name, columns=columns_def))

    def execute_update(self, sql: str):
        cursor = self._connection.cursor()
        cursor.execute(sql)
        self._connection.commit()

    def execute_query(self, sql: str):
        cursor = self._connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def execute_query_one(self, sql: str):
        cursor = self._connection.cursor()
        cursor.execute(sql)
        return cursor.fetchone()

    def close(self):
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class SqliteKeyStore(KeyStore):
    TABLE_COLUMNS_DEFINITION = "(key TEXT PRIMARY KEY, value TEXT)"
    PUT_QUERY = "INSERT OR REPLACE INTO {table} (key, value) VALUES ('{key}', '{value}')"
    GET_QUERY = "SELECT value FROM {table} WHERE key = '{key}'"

    def __init__(self, sql_executor: SqlExecutor, table_name: str):
        self._sql_executor = sql_executor
        self._table_name = table_name

    def put(self, key: str, data: str):
        self._sql_executor.execute_update(self.PUT_QUERY.format(table=self._table_name,
                                                                key=key,
                                                                value=data))

    def get(self, key: str) -> Optional[str]:
        result = self._sql_executor.execute_query_one(self.GET_QUERY.format(table=self._table_name,
                                                                            key=key))
        if result is None:
            return None

        return result[0]


class SqliteRowIterator(Iterator):

    def __init__(self, sql_executor: SqlExecutor, table_name: str, adapter: Adapter):
        self._sql_executor = sql_executor
        self._table_name = table_name
        self._adapter = adapter
        self._data = self._sql_executor.execute_query("SELECT rowid, * FROM {}".format(self._table_name))
        self._idx = -1
        self._to_delete = []

    def next(self) -> Optional:
        self._idx += 1
        if self._idx >= len(self._data):
            return None

        return self._adapter.from_raw(self._data[self._idx][1:])

    def delete(self):
        id = self._data[self._idx][0]
        self._to_delete.append(id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self._to_delete) == 0:
            return

        self._sql_executor.execute_update("DELETE FROM {} WHERE rowid IN ({})"
                                          .format(self._table_name, ','.join([str(i) for i in self._to_delete])))


class SqliteStore(Store):

    def __init__(self, sql_executor: SqlExecutor, table_name: str, adapter: Adapter):
        self._sql_executor = sql_executor
        self._table_name = table_name
        self._adapter = adapter

    def store(self, data):
        raw_data = self._adapter.to_raw(data)
        in_format = []
        for d in raw_data:
            if type(d) in (int, float):
                in_format.append(str(d))
            else:
                in_format.append("'{}'".format(str(d)))

        self._sql_executor.execute_update("INSERT INTO {} VALUES ({})".format(self._table_name,
                                                                              ','.join(in_format)))

    def iterator(self) -> Iterator:
        return SqliteRowIterator(self._sql_executor, self._table_name, self._adapter)
