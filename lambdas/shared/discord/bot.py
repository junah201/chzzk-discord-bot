import json
import logging

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from shared.discord.dataclass import INTERACTION_CALLBACK_TYPE

EPHEMERAL = 64

PONG = {"type": INTERACTION_CALLBACK_TYPE.PONG}
INVALID_SIGNATURE_RESPONSE = {"statusCode": 401, "body": "Invalid request signature"}

logger = logging.getLogger()


def verify_signature(public_key: str, headers: dict, raw_body: str) -> bool:
    signature = headers.get("x-signature-ed25519")
    timestamp = headers.get("x-signature-timestamp")
    try:
        VerifyKey(bytes.fromhex(public_key)).verify(
            f"{timestamp}{raw_body}".encode(), bytes.fromhex(signature)
        )
    except BadSignatureError as e:
        logger.info(
            json.dumps(
                {"type": "INVALID_REQUEST_SIGNATURE", "exception": str(e)},
                ensure_ascii=False,
            )
        )
        return False
    return True


def reply(
    content: str | None = None,
    *,
    embeds: list[dict] | None = None,
    components: list[dict] | None = None,
    ephemeral: bool = False,
) -> dict:
    data = {}
    if content is not None:
        data["content"] = content
    if embeds is not None:
        data["embeds"] = embeds
    if components is not None:
        data["components"] = components
    if ephemeral:
        data["flags"] = EPHEMERAL
    return {"type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE, "data": data}
