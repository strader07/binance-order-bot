from bot.commands import Command
from bot.orders.order import Order, OrderTarget, OrderType, OrderStatus, OrderStatusType

BUY_ORDER_FILLED = {
    "can_handle": [
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1)], OrderType.BUY, 'source'),
            OrderStatus(OrderStatusType.FILLED, 12345),
            True
        ),
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1), OrderTarget(46, 0.2)], OrderType.SELL, 'source'),
            OrderStatus(OrderStatusType.FILLED, 456),
            False
        ),
        (
            Order('12345675', 'HS', [], OrderType.BUY, 'source'),
            OrderStatus(OrderStatusType.NEW, 456),
            False
        )
    ],
    "handle": [
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1)], OrderType.BUY, 'source'),
            OrderStatus(OrderStatusType.FILLED, 12345),
            Command('ABC', [OrderTarget(123, 0.1)], OrderType.SELL, 'source')
        )
    ]
}

SELL_ORDER_FILLED = {
    "can_handle": [
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1)], OrderType.BUY, 'source'),
            OrderStatus(OrderStatusType.FILLED, 12345),
            False
        ),
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1), OrderTarget(46, 0.2)], OrderType.SELL, 'source'),
            OrderStatus(OrderStatusType.FILLED, 456),
            True
        ),
        (
            Order('12345675', 'HS', [], OrderType.BUY, 'source'),
            OrderStatus(OrderStatusType.NEW, 456),
            False
        )
    ],
    "handle": [
        (
            Order('123456', 'ABC', [OrderTarget(123, 0.1), OrderTarget(46, 0.2)], OrderType.SELL, 'source'),
            OrderStatus(OrderStatusType.FILLED, 456)
        )
    ]
}
