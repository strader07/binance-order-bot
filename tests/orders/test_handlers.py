import pytest
from mockito import mock, verify

from bot.commands.queue import CommandQueue
from bot.orders.tracking.handlers import BuyOrderFilledHandler, SellOrderFilledHandler
from bot.orders.tracking.reporter import OrderCompletionReporter

from tests.data_examples.order_handlers_data import BUY_ORDER_FILLED, SELL_ORDER_FILLED


# noinspection PyMethodMayBeStatic
class TestBuyOrderFilledHandler(object):

    @pytest.mark.parametrize("order,status,expected", BUY_ORDER_FILLED['can_handle'])
    def test_can_handle_order_and_status_returns_expected(self, order, status, expected):
        queue = mock(spec=CommandQueue)
        handler = BuyOrderFilledHandler(queue)

        assert handler.can_handle(order, status) == expected

    @pytest.mark.parametrize("order,status,expected", BUY_ORDER_FILLED['handle'])
    def test_handle_order_and_status_adds_command(self, order, status, expected):
        queue = mock(spec=CommandQueue)
        handler = BuyOrderFilledHandler(queue)

        handler.handle(order, status)
        verify(queue, times=1).store(expected)


class TestSellOrderFilledHandler(object):

    @pytest.mark.parametrize("order,status,expected", SELL_ORDER_FILLED['can_handle'])
    def test_can_handle_order_and_status_returns_expected(self, order, status, expected):
        reporter = mock(spec=OrderCompletionReporter)
        handler = SellOrderFilledHandler(reporter)

        assert handler.can_handle(order, status) == expected

    @pytest.mark.parametrize("order,status", SELL_ORDER_FILLED['handle'])
    def test_handle_order_and_status_reports(self, order, status):
        reporter = mock(spec=OrderCompletionReporter)
        handler = SellOrderFilledHandler(reporter)

        handler.handle(order, status)
        verify(reporter, times=1).order_completed(order)
