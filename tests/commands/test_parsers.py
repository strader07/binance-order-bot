from typing import List

import pytest

from bot.commands import Message
from bot.commands.parsers import CommandParserZhalgoul, CommandParserBPS
from bot.orders.order import OrderType, OrderTarget
from tests.data_examples.command_data import ZAGHLOUL_MESSAGES, BPS_MESSAGES


def assert_targets_prices_equal(expected: List[OrderTarget], actual):
    matches_found = 0
    for target in expected:
        for price in actual:
            if target.price_end == price:
                matches_found += 1
                break

    assert matches_found == len(actual)


class TestParserZhalgoul(object):

    @pytest.mark.parametrize("data", ZAGHLOUL_MESSAGES['valid'])
    def test_can_parse_valid_message_returns_true(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserZhalgoul()
        assert parser.can_parse(message)

    @pytest.mark.parametrize("data", ZAGHLOUL_MESSAGES['bad_data'])
    def test_can_parse_valid_header_bad_message_returns_true(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserZhalgoul()
        assert parser.can_parse(message)

    @pytest.mark.parametrize("data", BPS_MESSAGES['valid'])
    def test_can_parse_invalid_header_returns_false(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserZhalgoul()
        assert not parser.can_parse(message)

    @pytest.mark.parametrize("data", ZAGHLOUL_MESSAGES['valid'])
    def test_parse_valid_message_parses_correctly(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserZhalgoul()
        command = parser.parse(message)

        assert command.type == OrderType.BUY
        assert command.symbol == data['symbol']
        assert command.source_name == data['source_name']
        assert_targets_prices_equal(command.targets, data['targets'])

    @pytest.mark.parametrize("data", ZAGHLOUL_MESSAGES['bad_data'])
    def test_parse_bad_messages_raises_error(self, data):
        with pytest.raises(Exception):
            message = Message(data['message'], data['source_name'])

            parser = CommandParserZhalgoul()
            parser.parse(message)


class TestParserBPS(object):

    @pytest.mark.parametrize("data", BPS_MESSAGES['valid'])
    def test_can_parse_valid_message_returns_true(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserBPS()
        assert parser.can_parse(message)

    @pytest.mark.parametrize("data", BPS_MESSAGES['bad_data'])
    def test_can_parse_valid_header_bad_message_returns_true(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserBPS()
        assert parser.can_parse(message)

    @pytest.mark.parametrize("data", ZAGHLOUL_MESSAGES['valid'])
    def test_can_parse_invalid_header_returns_false(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserBPS()
        assert not parser.can_parse(message)

    @pytest.mark.parametrize("data", BPS_MESSAGES['valid'])
    def test_parse_valid_message_parses_correctly(self, data):
        message = Message(data['message'], data['source_name'])

        parser = CommandParserBPS()
        command = parser.parse(message)

        assert command.type == OrderType.BUY
        assert command.symbol == data['symbol']
        assert command.source_name == data['source_name']
        assert_targets_prices_equal(command.targets, data['targets'])

    @pytest.mark.parametrize("data", BPS_MESSAGES['bad_data'])
    def test_parse_bad_messages_raises_error(self, data):
        with pytest.raises(Exception):
            message = Message(data['message'], data['source_name'])

            parser = CommandParserBPS()
            parser.parse(message)
