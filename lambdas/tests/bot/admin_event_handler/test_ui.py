from bot.admin_event_handler.ui import parse_modal_values, reply
from shared import INTERACTION_CALLBACK_TYPE


def test_reply():
    assert reply("hi") == {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {"content": "hi"},
    }


def test_ephemeral_reply():
    assert reply("hi", ephemeral=True)["data"] == {"content": "hi", "flags": 64}


def test_parse_modal_values():
    components = [
        {"component": {"custom_id": "text", "value": "a"}},
        {"component": {"custom_id": "select", "values": ["b"]}},
        {"component": {"custom_id": "empty"}},
        {},
    ]

    assert parse_modal_values(components) == {"text": "a", "select": "b"}
