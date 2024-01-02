import json
import os

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

def middleware(event, context):
    print(f"event: {event}")
    print(event["rowBody"])

    # verify the signature
    try:
        raw_body = event.get("rawBody")
        auth_sig = event['params']['header'].get('x-signature-ed25519')
        auth_ts = event['params']['header'].get('x-signature-timestamp')

        message = auth_ts.encode() + raw_body.encode()
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(
            message,
            bytes.fromhex(auth_sig)
        )  # raises an error if unequal
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # ping pong
    body = event.get("body", {})
    if body.get("type") == TYPE.PING:
        return {
            "type": 1
        }

    # event handler
    custom_id = body.get("data", {}).get("custom_id", None)
    print(f"{custom_id=}")

    match custom_id:
        case _:
            # invalid custom_id
            return {
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"{custom_id=}\n\n```{event.get('rawBody')}```",
                }
            }


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return res
