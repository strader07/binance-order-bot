import pytest

from bot.commands.message import MessageParser, Message

# Needed for the fixtures
# noinspection PyUnresolvedReferences
from tests.telegram_fixtures import telegram_api


@pytest.mark.telegram_read
class TestTelegramApi(object):

    @pytest.fixture(scope='class')
    def expected_data(self):
        return [
            Message("some test text", "Tom Tzook"),
            Message("another test text", "Tom Tzook"),
        ]

    @pytest.fixture(scope='class')
    def wanted_offset(self):
        return 56366996

    @pytest.fixture(scope='class')
    def parser(self):
        return MessageParser()

    def test_get_updates_gets_all_expected_updates(self, telegram_api, parser, expected_data, wanted_offset):
        updates = telegram_api.get_updates(offset=wanted_offset)
        actual = parser.parse_all(updates)
        assert actual == expected_data
