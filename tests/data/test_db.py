import pytest

from bot.data.adapters import Adapter
from bot.data.db import SqliteKeyStore, SqliteStore, SqliteRowIterator

# Needed for the fixtures
# noinspection PyUnresolvedReferences
from tests.db_fixtures import temp_db_executor, temp_db_file


class FakeAdapter(Adapter):

    def to_raw(self, obj):
        return obj

    def from_raw(self, raw):
        return list(raw)


@pytest.fixture(scope='function')
def adapter():
    return FakeAdapter()


class TestSqlExecutor(object):

    def test_create_table_allows_querying_new_table(self, temp_db_executor):
        table_name = 'some_table'
        table_def = '(key TEXT, value TEXT)'

        temp_db_executor.create_table(table_name, table_def)

        result = temp_db_executor.execute_query("SELECT * FROM {}".format(table_name))
        assert len(result) == 0

    def test_create_table_and_insert_allows_querying_new_table(self, temp_db_executor):
        table_name = 'some_table'
        table_def = '(key TEXT, value TEXT)'
        key = 'some key'
        value = 'some value'

        temp_db_executor.create_table(table_name, table_def)
        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(table_name, key, value))

        result = temp_db_executor.execute_query_one("SELECT * FROM {}".format(table_name))
        assert result[0] == key
        assert result[1] == value


class TestSqliteKeyStore(object):

    @pytest.fixture(scope='function')
    def keystore_table(self, temp_db_executor):
        table_name = 'key_store'
        temp_db_executor.create_table(table_name, SqliteKeyStore.TABLE_COLUMNS_DEFINITION)
        return table_name

    def test_put_no_key_before_inserted_to_table(self, temp_db_executor, keystore_table):
        key = 'some key'
        value = 'some value'

        store = SqliteKeyStore(temp_db_executor, keystore_table)
        store.put(key, value)

        result = temp_db_executor.execute_query_one("SELECT * FROM {}".format(keystore_table))
        assert result[0] == key
        assert result[1] == value

    def test_put_key_existed_updates_table(self, temp_db_executor, keystore_table):
        key = 'some key'
        value = 'some value'
        value2 = 'balalala'

        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(keystore_table, key, value))

        store = SqliteKeyStore(temp_db_executor, keystore_table)
        store.put(key, value2)

        result = temp_db_executor.execute_query_one("SELECT * FROM {}".format(keystore_table))
        assert result[0] == key
        assert result[1] == value2

    def test_put_has_another_key_key_existed_updates_correct_table(self, temp_db_executor, keystore_table):
        key = 'some key'
        value = 'some value'
        value2 = 'balalala'
        key2 = 'some key 23'
        value_key2 = 'some value 131'

        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(keystore_table, key, value))
        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(keystore_table, key2, value_key2))

        store = SqliteKeyStore(temp_db_executor, keystore_table)
        store.put(key, value2)

        result = temp_db_executor.execute_query_one("SELECT * FROM {} WHERE key='{}'".format(keystore_table, key))
        assert result[0] == key
        assert result[1] == value2

        result = temp_db_executor.execute_query_one("SELECT * FROM {} WHERE key='{}'".format(keystore_table, key2))
        assert result[0] == key2
        assert result[1] == value_key2

    def test_get_key_not_in_table_returns_none(self, temp_db_executor, keystore_table):
        key = 'some key'

        store = SqliteKeyStore(temp_db_executor, keystore_table)

        assert store.get(key) is None

    def test_get_key_in_table_returns_value(self, temp_db_executor, keystore_table):
        key = 'some key'
        value = 'some value'

        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(keystore_table, key, value))

        store = SqliteKeyStore(temp_db_executor, keystore_table)

        assert store.get(key) == value

    def test_get_key_in_table_and_updated_returns_value(self, temp_db_executor, keystore_table):
        key = 'some key'
        value = 'some value'
        value2 = 'some adasfasfa value'

        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', '{}')".format(keystore_table, key, value))

        store = SqliteKeyStore(temp_db_executor, keystore_table)

        assert store.get(key) == value

        store.put(key, value2)

        assert store.get(key) == value2


class TestSqliteStore(object):

    @pytest.fixture(scope='function')
    def store_table(self, temp_db_executor):
        table_name = 'store'
        temp_db_executor.create_table(table_name, "(some_str TEXT, some_int INTEGER)")
        return table_name

    @pytest.fixture(scope='function')
    def row_values(self):
        return ["hello from the other side", 231]

    def test_store_adds_new_row_to_table(self, temp_db_executor, store_table, adapter, row_values):
        store = SqliteStore(temp_db_executor, store_table, adapter)
        store.store(row_values)

        result = temp_db_executor.execute_query_one("SELECT * FROM {}".format(store_table))
        assert list(result) == row_values


class TestSqliteRowIterator(object):

    @pytest.fixture(scope='function')
    def table_with_values(self, temp_db_executor):
        table_name = 'store'
        values = ['some value mannn', 545]
        temp_db_executor.create_table(table_name, "(some_str TEXT, some_int INTEGER)")
        temp_db_executor.execute_update("INSERT INTO {} VALUES ('{}', {})"
                                        .format(table_name, values[0], values[1]))
        return table_name, values

    def test_next_returns_next_row(self, temp_db_executor, table_with_values, adapter):
        table_name, values = table_with_values
        iterator = SqliteRowIterator(temp_db_executor, table_name, adapter)

        assert iterator.next() == values

    def test_delete_deletes_row_on_context_exit(self, temp_db_executor, table_with_values, adapter):
        table_name, values = table_with_values
        with SqliteRowIterator(temp_db_executor, table_name, adapter) as iterator:
            iterator.next()
            iterator.delete()

        result = temp_db_executor.execute_query("SELECT * FROM {}".format(table_name))
        assert len(result) == 0
