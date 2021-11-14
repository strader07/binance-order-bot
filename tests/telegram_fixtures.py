import pytest

from bot.ui.telegram import TelegramApi


@pytest.fixture(scope='session')
def telegram_api(request):
    token = request.config.getoption('--bot-token')
    return TelegramApi(bot_token=token)
