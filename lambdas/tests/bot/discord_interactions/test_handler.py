import importlib
import json

import pytest
from nacl.signing import SigningKey
from shared import INTERACTION_CALLBACK_TYPE, TYPE

discord_interactions = importlib.import_module("bot.discord_interactions")

SIGNING_KEY = SigningKey.generate()


@pytest.fixture(autouse=True)
def public_key(monkeypatch):
    monkeypatch.setattr(
        discord_interactions,
        "DISCORD_PUBLIC_KEY",
        SIGNING_KEY.verify_key.encode().hex(),
    )


def signed_event(body: dict, key: SigningKey = SIGNING_KEY) -> dict:
    raw_body = json.dumps(body)
    timestamp = "1700000000"
    signature = key.sign(f"{timestamp}{raw_body}".encode()).signature.hex()
    return {
        "headers": {
            "x-signature-ed25519": signature,
            "x-signature-timestamp": timestamp,
        },
        "body": raw_body,
    }


def test_ping_is_answered_with_pong():
    res = discord_interactions.handler(signed_event({"type": TYPE.PING}), None)

    assert res["statusCode"] == 200
    assert json.loads(res["body"]) == {"type": 1}


@pytest.mark.parametrize(
    "tamper",
    [
        lambda e: e.update(body=json.dumps({"type": TYPE.APPLICATION_COMMAND})),
        lambda e: e["headers"].update({"x-signature-timestamp": "1700000001"}),
    ],
    ids=["body", "timestamp"],
)
def test_tampered_request_is_401(tamper):
    event = signed_event({"type": TYPE.PING})
    tamper(event)

    res = discord_interactions.handler(event, None)

    assert res["statusCode"] == 401


def test_signed_with_other_key_is_401():
    event = signed_event({"type": TYPE.PING}, key=SigningKey.generate())

    res = discord_interactions.handler(event, None)

    assert res["statusCode"] == 401


def test_commands_point_to_dashboard():
    res = discord_interactions.handler(
        signed_event({"type": TYPE.APPLICATION_COMMAND, "data": {"name": "알림"}}),
        None,
    )

    body = json.loads(res["body"])
    assert res["statusCode"] == 200
    assert body["type"] == INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE
    button = body["data"]["components"][0]["components"][0]
    assert button["url"] == "https://chzzk.junah.dev"
