import logging
import time
from typing import List, Dict, Tuple
import enum

# Requirement is python-binance, not binance
from binance.client import Client
from binance.enums import *

from bot.commands.command import Command
from bot.orders.order import Order, OrderStatus, OrderTarget, OrderStatusType


class FilterType(enum.Enum):
    PRICE_FILTER = 'PRICE_FILTER'


class Binance(object):
    _DEFAULT_QTY_PERCENTAGE = 0.2
    _DEFAULT_STOP_PRICE_OFFSET = 3

    def __init__(self, client: Client, logger: logging.Logger, test_order: bool = False):
        self._client = client
        self._logger = logger
        self._order_method = client.create_test_order if test_order else client.create_order
        self._time_offset = 500
        self.sync_time()

    def sync_time(self):
        server_time = self._client.get_server_time()['serverTime']
        local_time = int(time.time() * 1000)
        diff = local_time - server_time
        if diff > 0:
            self._time_offset = diff
        else:
            self._time_offset = 500

    def place_buy_order(self, command: Command, qty_percentage: float = None) -> Order:
        if qty_percentage is None:
            qty_percentage = self._DEFAULT_QTY_PERCENTAGE

        symbol_btc = command.symbol + 'BTC'

        price = self._get_price_for_symbol(symbol_btc)
        balance = self._client.get_asset_balance(asset='BTC', timestamp=self._get_timestamp())
        if balance is None:
            raise ValueError('BTC balance is None')
        balance = balance['free']

        balance_to_use = float(balance) * qty_percentage
        quantity = int(balance_to_use / float(price))

        self._logger.debug('Ordering: SELL %s, qty: %d, price: %s', symbol_btc, quantity,
                           balance_to_use)
        # noinspection PyArgumentList
        order_data = self._order_method(
            symbol=symbol_btc,
            side=SIDE_BUY,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price,
            timestamp=self._get_timestamp())

        return self._build_order(command, order_data)

    def place_sell_orders(self, command: Command, stop_price_offset: int = None) -> \
            Tuple[List[Tuple[Order, OrderTarget]], List[Tuple[OrderTarget, Exception]]]:
        if stop_price_offset is None:
            stop_price_offset = self._DEFAULT_STOP_PRICE_OFFSET

        symbol_btc = command.symbol + 'BTC'
        balance = self._client.get_asset_balance(asset=command.symbol, timestamp=self._get_timestamp())
        balance = balance['free']
        price = self._get_price_for_symbol(symbol_btc)

        orders = []
        failed = []
        for target in command.targets:
            try:
                order = self._place_sell_order(command, target, balance, price, stop_price_offset)
                orders.append((order, target))
            except Exception as e:
                self._logger.error('Error placing sell order %s (%s): %s',
                                   command, target, str(e))
                failed.append((target, e))

        return orders, failed

    def query_order_status(self, order: Order) -> OrderStatus:
        order_data = self._client.get_order(symbol=order.symbol + 'BTC',
                                            orderId=order.id,
                                            timestamp=self._get_timestamp())

        return OrderStatus(
            OrderStatusType.from_value(order_data['status']),
            int(order_data['time']))

    def _place_sell_order(self, command: Command, target: OrderTarget,
                          balance: str, price: str, stop_price_offset: int) -> Order:
        symbol_btc = command.symbol + 'BTC'
        limit_price = self._make_full_price_from_target(str(target.price_end), price)
        stop_price_end = self._modify_price_end(target.price_end, stop_price_offset)
        stop_price = self._make_full_price_from_target(stop_price_end, price)

        price_filter = self._get_filter(symbol_btc, FilterType.PRICE_FILTER)
        # float(filter['tickSize']) * round((stop - float(filter['minPrice']))/float(filter['tickSize']))
        stop_price = float(price_filter['tickSize']) * round(
            (float(stop_price) - float(price_filter['minPrice'])) / float(price_filter['tickSize']))
        stop_price = "{:.8f}".format(stop_price)
        limit_price = "{:.8f}".format(float(limit_price))

        quantity = int(float(balance) * target.qty_percentage)

        self._logger.debug('Ordering: SELL %s, qty: %d, stop: %s, limit: %s', symbol_btc, quantity,
                           stop_price, limit_price)
        # noinspection PyArgumentList
        order_data = self._order_method(
            symbol=symbol_btc,
            side=SIDE_SELL,
            type=ORDER_TYPE_TAKE_PROFIT_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price,
            timestamp=self._get_timestamp())

        return self._build_order(command, order_data)

    def _get_price_for_symbol(self, symbol) -> str:
        all_prices = self._client.get_all_tickers()
        matching_prices = [data['price'] for data in all_prices if data['symbol'] == symbol]
        if len(matching_prices) == 0:
            raise AssertionError('Unable to find price for symbol ' + symbol)

        return matching_prices[0]

    def _get_timestamp(self):
        return int((time.time() * 1000) - self._time_offset)

    def _get_filter(self, symbol: str, filter_type: FilterType):
        exchange_info = self._client.get_exchange_info()
        filters = [info['filters'] for info in exchange_info['symbols'] if info['symbol'] == symbol][0]
        return [filter for filter in filters if filter['filterType'] == filter_type.value][0]

    @staticmethod
    def _make_full_price_from_target(price_end: str, actual_price: str) -> str:
        index = [i for i in range(len(actual_price)) if actual_price[i] == '0'][-1]
        return actual_price[:index+1] + price_end

    @staticmethod
    def _modify_price_end(price_end: int, offset: int) -> str:
        digits = len(str(price_end))
        modified = str(price_end - offset)
        if len(modified) < digits:
            return ''.join(['0'] * (digits - len(modified))) + modified
        return modified

    @staticmethod
    def _build_order(command: Command, order_data: Dict) -> Order:
        return Order(order_id=order_data['orderId'],
                     symbol=command.symbol,
                     targets=command.targets,
                     type=command.type,
                     source_name=command.source_name)
