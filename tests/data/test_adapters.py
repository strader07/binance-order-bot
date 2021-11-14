import pytest

from bot.data.adapters import OrderToSheetRowAdpater, CommandToSheetRowAdapter
from tests.data_examples.data_adapters_data import ORDER_TO_SHEET_DATA, COMMAND_TO_SHEET_DATA


class TestOrderToSheetRowAdpater(object):

    @pytest.mark.parametrize("raw,obj", ORDER_TO_SHEET_DATA)
    def test_to_raw_converts_to_expected(self, raw, obj):
        adapter = OrderToSheetRowAdpater()
        result = adapter.to_raw(obj)
        assert result == raw

    @pytest.mark.parametrize("raw,obj", ORDER_TO_SHEET_DATA)
    def test_from_raw_converts_to_expected(self, raw, obj):
        adapter = OrderToSheetRowAdpater()
        result = adapter.from_raw(raw)

        assert result == obj


class TestCommandToSheetRowAdapter(object):

    @pytest.mark.parametrize("raw,obj", COMMAND_TO_SHEET_DATA)
    def test_to_raw_converts_to_expected(self, raw, obj):
        adapter = CommandToSheetRowAdapter()
        result = adapter.to_raw(obj)
        assert result == raw

    @pytest.mark.parametrize("raw,obj", COMMAND_TO_SHEET_DATA)
    def test_from_raw_converts_to_expected(self, raw, obj):
        adapter = CommandToSheetRowAdapter()
        result = adapter.from_raw(raw)

        assert result == obj
