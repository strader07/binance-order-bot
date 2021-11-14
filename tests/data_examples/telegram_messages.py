FROM_USER_DATA_FORMAT = """
{{
    "update_id": 24063093,
    "message": {{
        "message_id": 15894,
        "from": {{
            "id": 123456789,
            "is_bot": false,
            "first_name": "{first_name}",
            "last_name": "{last_name}",
            "username": "GarbageUsername",
            "language_code": "en-US"
        }},
        "chat": {{
            "id": 123456789,
            "first_name": "{first_name}",
            "last_name": "{last_name}",
            "username": "GarbageUsername",
            "type": "private"
        }},
        "date": 1506207666,
        "text": "{text}"
    }}
}}
"""

FORWARDED_FROM_CHAT_DATA_FORMAT = """
{{
    "update_id": 24063093,
    "message": {{
        "message_id": 15894,
        "from": {{
            "id": 123456789,
            "is_bot": false,
            "first_name": "{first_name}",
            "last_name": "{last_name}",
            "username": "GarbageUsername",
            "language_code": "en-US"
        }},
        "chat": {{
            "id": 123456789,
            "first_name": "{first_name}",
            "last_name": "{last_name}",
            "username": "GarbageUsername",
            "type": "private"
        }},
        "forward_from_chat": {{
            "id": 12346124,
            "title": "{title}",
            "type": "channel"
        }},
        "date": 1506207666,
        "text": "{text}"
    }}
}}
"""
