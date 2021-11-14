import gspread
import pytest
import random

from tests.data_examples.sheets_spreadsheet_data import READ_SHEET_NAME, SPREADSHEET_ID


def random_sheet_name():
    return str(random.randint(0, 10000))


@pytest.fixture(scope='session')
def spreadsheet(request):
    secrets = request.config.getoption('--sheets-secrets-file')
    gs = gspread.service_account(filename=secrets)
    return gs.open_by_key(SPREADSHEET_ID)


@pytest.fixture(scope='session')
def read_sheet(spreadsheet):
    return spreadsheet.worksheet(READ_SHEET_NAME)


@pytest.fixture(scope='function')
def write_sheet_single_row(spreadsheet):
    sheet_name = random_sheet_name()
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=13)
    yield sheet, sheet_name
    spreadsheet.del_worksheet(sheet)


@pytest.fixture(scope='function')
def delete_sheet_single_row(spreadsheet):
    sheet_name = random_sheet_name()
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows=2, cols=4)
    sheet.append_row(['some', 'data', 'in', 'row'])
    yield sheet
    spreadsheet.del_worksheet(sheet)
