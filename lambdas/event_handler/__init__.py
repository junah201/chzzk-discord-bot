import json
import os
import logging

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from shared import INTERACTION_CALLBACK_TYPE, TYPE, middleware


DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
def handler(event, context):
    # verify the signature
    try:
        raw_body = event['body']
        signature = event['headers'].get('x-signature-ed25519')
        timestamp = event['headers'].get('x-signature-timestamp')

        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(
            f"{timestamp}{raw_body}".encode(),
            bytes.fromhex(signature)
        )
    except BadSignatureError as e:
        logger.info(
            json.dumps(
                {
                    "type": "INVALID_REQUEST_SIGNATURE",
                    "exception": str(e)
                },
                ensure_ascii=False
            )
        )
        return {
            "statusCode": 401,
            "body": "Invalid request signature"
        }

    # ping pong
    body = json.loads(raw_body)
    logging.info(
        json.dumps(
            {
                "type": "REQUEST_BODY",
                "body": raw_body
            },
            ensure_ascii=False
        )
    )

    if body.get("type") == TYPE.PING:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "type": 1
                },
                ensure_ascii=False
            )
        }

    # 슬래시 명령어 지원 종료 (from 2024.07.06)
    res = {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "embeds": [
                {
                    "title": "슬래시 명령어 지원 종료 안내",
                    "description": "`**2024.07.06**부터 치직 봇은 슬래시 명령어를 지원하지 않습니다. 이제부터는 [치직 봇 웹사이트](https://chzzk.junah.dev)를 사용해주세요. 또한 [치직 봇 공식 서버](https://api.chzzk.junah.dev/support-server)에서 도움을 받을 수 있습니다.",
                    "color": 0x02E895,
                    "footer": {
                        "text": "치직 chzzk.junah.dev"
                    }
                }
            ],
        }
    }
    return {
        "statusCode": 200,
        "body": json.dumps(res, ensure_ascii=False)
    }
