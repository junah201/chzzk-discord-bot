import json
import os

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import events

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")


def middleware(event, context):
    print(f"event: {event}")
    print(json.dumps(event))

    # verify the signature
    try:
        raw_body = event['body']
        auth_sig = event['headers'].get('x-signature-ed25519')
        auth_ts = event['headers'].get('x-signature-timestamp')

        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(
            f'{auth_ts}{raw_body}'.encode(),
            bytes.fromhex(auth_sig)
        )
    except Exception as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # ping pong
    body = json.loads(raw_body)
    print("=== body ===")
    print(body)

    if body.get("type") == TYPE.PING:
        return {
            'type': 1
        }

    # event handler
    command_name = body.get("data", {}).get("name", None)
    print(f"{command_name=}")

    match command_name:
        case COMMAND_NAME.ADD_NOTIFICATION:
            return events.add_notification.handler(event, context)
        case COMMAND_NAME.DELETE_NOTIFICATION:
            return events.delete_notification.handler(event, context)
        case _:
            # invalid custom_id
            return {
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"{command_name=}\n\n```json\n{event.get('body')}```",
                }
            }


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return {
        'statusCode': 200,
        'body': json.dumps(res)
    }
