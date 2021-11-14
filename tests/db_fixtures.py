import pytest
import tempfile

from bot.data.db import SqlExecutor


@pytest.fixture(scope='function')
def temp_db_file():
    with tempfile.NamedTemporaryFile(suffix='.db') as file:
        yield file.name


@pytest.fixture(scope='function')
def temp_db_executor(temp_db_file):
    with SqlExecutor(temp_db_file) as executor:
        yield executor
