import json
import os
import logging
import traceback

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from shared import INTERACTION_CALLBACK_TYPE, TYPE, middleware
from .events import add_notification, delete_notification
from dataclasses import dataclass


DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class COMMAND_NAME:
    ADD_NOTIFICATION: str = "알림추가"
    DELETE_NOTIFICATION: str = "알림삭제"


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

    # event handler
    command_name = body.get("data", {}).get("name", None)
    logging.info(
        json.dumps(
            {
                "type": "COMMAND_NAME",
                "name": command_name
            },
            ensure_ascii=False
        )
    )

    try:
        res = {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"{command_name=}\n\n```json\n{event.get('body')}```",
            }
        }
        match command_name:
            case COMMAND_NAME.ADD_NOTIFICATION:
                res = add_notification.handler(event, context)
            case COMMAND_NAME.DELETE_NOTIFICATION:
                res = delete_notification.handler(event, context)

        return {
            "statusCode": 200,
            "body": json.dumps(res, ensure_ascii=False)
        }

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "EVENT_HANDLER_ERROR",
                    "exception": str(e),
                    "traceback": traceback.format_exc()
                },
                ensure_ascii=False
            )
        )
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {
                        "embeds": [
                            {
                                "title": f"알 수 없는 오류 발생",
                                "description": f"```{e}```\n\n계속해서 문제가 발생한다면 대신 [치직 봇 웹사이트](https://chzzk.junah.dev)를 사용해주세요.\n또한 [치직 봇 공식 서버](https://api.chzzk.junah.dev/support-server)에서 도움을 받을 수 있습니다.",
                                "color": 0xF01D15,
                                "footer": {
                                    "text": "치직"
                                }
                            },
                        ],
                    }
                }
            ),
        }
