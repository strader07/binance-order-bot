from typing import Optional

from bot.data.adapters import Adapter
from bot.data.store import Store

import gspread

from bot.util.iterator import Iterator


class SheetRowIterator(Iterator):

    def __init__(self, sheet, row_parser, start_index: int = 0):
        self._sheet = sheet
        self._row_parser = row_parser
        self._start_index = start_index
        self._idx = start_index
        self._to_remove = []

    def next(self) -> Optional:
        self._idx += 1
        row_values = self._sheet.row_values(self._idx)
        if len(row_values) == 0:
            return None

        return self._row_parser(row_values)

    def delete(self):
        self._to_remove.append(self._idx)

    def __enter__(self):
        self._idx = self._start_index
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for idx in self._to_remove:
            self._sheet.delete_rows(idx)


class SheetsStore(Store):

    def __init__(self, spreadsheet, sheet_name: str, adapter: Adapter):
        self._spreadsheet = spreadsheet
        self._sheet_name = sheet_name
        self._adapter = adapter

    def store(self, data):
        sheet = self._spreadsheet.worksheet(self._sheet_name)
        sheet.append_row(self._adapter.to_raw(data))

    def iterator(self) -> Iterator:
        sheet = self._spreadsheet.worksheet(self._sheet_name)
        return SheetRowIterator(sheet, self._adapter.from_raw)


class Spreadsheet(object):

    def __init__(self, spreadsheet_id, client_secrets_path):
        self._spreadsheet_id = spreadsheet_id
        self._client_secrets_path = client_secrets_path

    def open(self):
        gs = gspread.service_account(filename=self._client_secrets_path)
        return gs.open_by_key(self._spreadsheet_id)
