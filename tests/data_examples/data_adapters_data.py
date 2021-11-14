from bot.commands import Command
from bot.orders.order import Order, OrderTarget, OrderType

ORDER_TO_SHEET_DATA = [
    (
        [
            "124564",
            OrderTarget.to_json([OrderTarget(123, 0.5), OrderTarget(654, 0.7), OrderTarget(675, 0.4)]),
            "some source",
            "AES",
            OrderType.BUY.value
        ],
        Order("124564",
              "AES",
              [OrderTarget(123, 0.5), OrderTarget(654, 0.7), OrderTarget(675, 0.4)],
              OrderType.BUY,
              "some source")
    ),
    (
        [
            "12456543",
            OrderTarget.to_json([OrderTarget(12676, 0.5), OrderTarget(120, 0.7)]),
            "somhsdf",
            "ASE",
            OrderType.SELL.value
        ],
        Order("12456543",
              "ASE",
              [OrderTarget(12676, 0.5), OrderTarget(120, 0.7)],
              OrderType.SELL,
              "somhsdf")
    ),
]

COMMAND_TO_SHEET_DATA = [
    (
        [
            "AES",
            OrderTarget.to_json([OrderTarget(123, 0.5), OrderTarget(654, 0.7), OrderTarget(675, 0.4)]),
            "some source",
            OrderType.BUY.value,
            -1
        ],
        Command("AES",
                [OrderTarget(123, 0.5), OrderTarget(654, 0.7), OrderTarget(675, 0.4)],
                OrderType.BUY,
                "some source")
    ),
    (
        [
            "ASE",
            OrderTarget.to_json([OrderTarget(12676, 0.5), OrderTarget(120, 0.7)]),
            "somhsdf",
            OrderType.SELL.value,
            -1
        ],
        Command("ASE",
                [OrderTarget(12676, 0.5), OrderTarget(120, 0.7)],
                OrderType.SELL,
                "somhsdf")
    )
]
