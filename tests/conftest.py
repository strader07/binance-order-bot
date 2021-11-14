import json
import os

import pytest
import settings


def load_config(config):
    if not os.path.exists(settings.CONFIG_FILE):
        return

    with open(settings.CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    if not config.option.sheets_secrets_file:
        config.option.sheets_secrets_file = config_data['sheets_secrets_path']

    if not config.option.bot_token and not config.option.bot_token_file:
        config.option.bot_token = config_data['bot_token']


def pytest_addoption(parser):
    parser.addoption('--sheets', action='store_true', dest="sheets",
                     default=False, help="enable sheets test")
    parser.addoption('--sheets-secrets-file', action='store', dest="sheets_secrets_file",
                     default=None, help="file containing secrets and auth for gspread api")
    parser.addoption('--telegram-read', action='store_true', dest="telegram_read",
                     default=False, help="enable telegram reading tests")
    parser.addoption('--bot-token', action='store', dest="bot_token",
                     default=None, help="token for the telegram bot")
    parser.addoption('--bot-token-file', action='store', dest="bot_token_file",
                     default=None, help="file containing the token for the telegram bot")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "sheets: mark test that uses google spreadsheets"
    )
    config.addinivalue_line(
        "markers", "telegram_read: mark test that read from the telegram API"
    )

    load_config(config)

    if config.option.bot_token_file and not config.option.bot_token:
        with open(config.option.bot_token_file, 'r') as f:
            config.option.bot_token = f.read()

    if config.option.sheets and not config.option.sheets_secrets_file:
        raise AssertionError('--sheets-secrets-file required')

    if config.option.telegram_read and not config.option.bot_token:
        raise AssertionError('--bot-token or --bot-token-file required')


def pytest_collection_modifyitems(config, items):
    custom_marks = [('sheets', config.option.sheets), ('telegram_read', config.option.telegram_read)]
    for name, option in custom_marks:
        if option:
            continue

        skip_marker = pytest.mark.skip(reason='{} not selected'.format(name))
        for item in items:
            if name in item.keywords:
                item.add_marker(skip_marker)
