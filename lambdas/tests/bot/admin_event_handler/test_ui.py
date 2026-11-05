from bot.admin_event_handler.ui import parse_modal_values


def test_parse_modal_values():
    components = [
        {"component": {"custom_id": "text", "value": "a"}},
        {"component": {"custom_id": "select", "values": ["b"]}},
        {"component": {"custom_id": "empty"}},
        {},
    ]

    assert parse_modal_values(components) == {"text": "a", "select": "b"}
