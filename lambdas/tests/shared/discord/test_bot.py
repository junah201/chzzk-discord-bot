import pytest
from nacl.signing import SigningKey
from shared import INTERACTION_CALLBACK_TYPE
from shared.discord.bot import reply, verify_signature

SIGNING_KEY = SigningKey.generate()
PUBLIC_KEY = SIGNING_KEY.verify_key.encode().hex()
TIMESTAMP = "1700000000"
RAW_BODY = '{"type": 1}'


def headers(key: SigningKey = SIGNING_KEY, timestamp: str = TIMESTAMP) -> dict:
    signature = key.sign(f"{timestamp}{RAW_BODY}".encode()).signature.hex()
    return {"x-signature-ed25519": signature, "x-signature-timestamp": timestamp}


def test_valid_signature():
    assert verify_signature(PUBLIC_KEY, headers(), RAW_BODY) is True


@pytest.mark.parametrize(
    ("request_headers", "raw_body"),
    [
        (headers(), '{"type": 2}'),
        ({**headers(), "x-signature-timestamp": "1700000001"}, RAW_BODY),
        (headers(key=SigningKey.generate()), RAW_BODY),
    ],
    ids=["body", "timestamp", "other_key"],
)
def test_invalid_signature(request_headers, raw_body):
    assert verify_signature(PUBLIC_KEY, request_headers, raw_body) is False


def test_reply():
    assert reply("hi") == {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {"content": "hi"},
    }


def test_ephemeral_reply():
    assert reply("hi", ephemeral=True)["data"] == {"content": "hi", "flags": 64}


def test_reply_with_embeds_and_components():
    embeds = [{"title": "t"}]
    components = [{"type": 1, "components": []}]

    assert reply(embeds=embeds, components=components)["data"] == {
        "embeds": embeds,
        "components": components,
    }
