import pytest

from bot.data.adapters import Adapter
from bot.data.sheets import SheetsStore, SheetRowIterator
from tests.data_examples.sheets_spreadsheet_data import WRITE_DATA, READ_DATA

# Needed for the fixtures
# noinspection PyUnresolvedReferences
from tests.sheets_fixtures import spreadsheet, write_sheet_single_row, read_sheet, delete_sheet_single_row


class FakeAdapter(Adapter):

    def to_raw(self, obj):
        return obj

    def from_raw(self, raw):
        return raw


@pytest.mark.sheets
class TestSheetRowIterator(object):

    @pytest.fixture(scope='class')
    def row_parser(self):
        def parser(input):
            return input

        return parser

    @pytest.mark.parametrize("start_idx,expected_data", READ_DATA)
    def test_next_gets_next_row(self, read_sheet, row_parser, start_idx, expected_data):
        iterator = SheetRowIterator(read_sheet, row_parser, start_index=start_idx)
        value = iterator.next()

        assert value == expected_data

    def test_mark_delete_once_deletes_on_context_exit(self, row_parser, delete_sheet_single_row):
        with SheetRowIterator(delete_sheet_single_row, row_parser) as iterator:
            iterator.next()
            iterator.delete()

        assert len(delete_sheet_single_row.row_values(1)) == 0


@pytest.mark.sheets
class TestSheetsStore(object):

    @pytest.fixture(scope='class')
    def row_adapter(self):
        return FakeAdapter()

    @pytest.mark.parametrize("data", WRITE_DATA)
    def test_store_adds_new_data_to_sheet(self, spreadsheet, write_sheet_single_row, row_adapter, data):
        sheet, name = write_sheet_single_row
        store = SheetsStore(spreadsheet, name, row_adapter)
        store.store(data)

        assert sheet.row_values(1) == data
