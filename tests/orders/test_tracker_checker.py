import logging

import pytest
from mockito import when, verify, mock, spy2

from bot.orders.binance_api import Binance
from bot.orders.order import Order
from bot.orders.tracking.tracker import OrderTracker
from bot.orders.tracking.tracker_checker import OrderTrackingTask, OrderStatusHandler
from bot.util.iterator import EmptyIterator


class TestOrderTrackingTask(object):

    def test_do_check_checks_all_orders(self):
        orders = [
            mock(spec=Order),
            mock(spec=Order),
            mock(spec=Order)
        ]

        copy_orders = list(orders)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_orders.pop() if len(copy_orders) > 0 else None)

        order_tracker = mock(spec=OrderTracker)
        when(order_tracker).iterator().thenReturn(iterator)
        binance = mock(spec=Binance)
        handler = mock(spec=OrderStatusHandler)

        tracking_task = OrderTrackingTask(order_tracker, binance, handler, mock(spec=logging.Logger))
        spy2(tracking_task.check_order)
        tracking_task.do_check()

        verify(tracking_task, times=len(orders)).check_order(...)

    def test_do_check_deletes_handled_orders(self):
        orders = [
            mock(spec=Order),
            mock(spec=Order),
            mock(spec=Order)
        ]

        copy_orders = list(orders)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_orders.pop() if len(copy_orders) > 0 else None)

        order_tracker = mock(spec=OrderTracker)
        when(order_tracker).iterator().thenReturn(iterator)
        binance = mock(spec=Binance)
        handler = mock(spec=OrderStatusHandler)

        tracking_task = OrderTrackingTask(order_tracker, binance, handler, mock(spec=logging.Logger))
        spy2(tracking_task.check_order)
        when(tracking_task).check_order(...).thenReturn(True)
        tracking_task.do_check()

        verify(iterator, times=len(orders)).delete()

    def test_do_check_does_not_deletes_unhandled_orders(self):
        orders = [
            mock(spec=Order),
            mock(spec=Order),
            mock(spec=Order)
        ]

        copy_orders = list(orders)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_orders.pop() if len(copy_orders) > 0 else None)

        order_tracker = mock(spec=OrderTracker)
        when(order_tracker).iterator().thenReturn(iterator)
        binance = mock(spec=Binance)
        handler = mock(spec=OrderStatusHandler)

        tracking_task = OrderTrackingTask(order_tracker, binance, handler, mock(spec=logging.Logger))
        spy2(tracking_task.check_order)
        when(tracking_task).check_order(...).thenReturn(False)
        tracking_task.do_check()

        verify(iterator, times=0).delete()
