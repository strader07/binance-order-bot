from bot.commands.command import Command, OrderType
from bot.commands.queue import CommandQueue, CommandHandler
from bot.data.error import ErrorTracker
from bot.orders.binance_api import Binance
from bot.orders.order import OrderTarget
from bot.orders.tracking.tracker import OrderTracker


class BuyCommandHandler(CommandHandler):

    def __init__(self, order_tracker: OrderTracker, binance: Binance):
        self._order_tracker = order_tracker
        self._binance = binance

    def can_handle(self, command: Command) -> bool:
        return command.type == OrderType.BUY

    def handle(self, command: Command):
        order = self._binance.place_buy_order(command)
        self._order_tracker.store(order)


class SellCommandHandler(CommandHandler):

    def __init__(self, order_tracker: OrderTracker, binance: Binance, command_queue: CommandQueue,
                 error_tracker: ErrorTracker):
        self._order_tracker = order_tracker
        self._binance = binance
        self._command_queue = command_queue
        self._error_tracker = error_tracker

    def can_handle(self, command: Command) -> bool:
        return command.type == OrderType.SELL

    def handle(self, command: Command):
        orders, failed = self._binance.place_sell_orders(command)

        completed_percentage = 0

        for order, target in orders:
            completed_percentage += target.qty_percentage
            self._order_tracker.store(order)

        if len(orders) == 0 and len(failed) == len(command.targets):
            self._error_tracker.failed_sell_order(command, command.targets, [f[1] for f in failed])
            self._command_queue.store(command)
        else:
            remaining_percentage = 1 - completed_percentage

            for target, error in failed:
                new_target = OrderTarget(target.price_end, target.qty_percentage * remaining_percentage)
                new_command = Command(command.symbol, [new_target], OrderType.SELL, command.source_name)
                self._command_queue.store(new_command)

            self._error_tracker.failed_sell_order(command, [f[0] for f in failed], [f[1] for f in failed])
