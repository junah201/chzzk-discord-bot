import json
import logging
import os

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from shared import INTERACTION_CALLBACK_TYPE, TYPE, middleware
from shared.discord.dataclass import BUTTON_STYLE, COMPONENT_TYPE

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
def handler(event, context):
    # verify the signature
    try:
        raw_body = event["body"]
        signature = event["headers"].get("x-signature-ed25519")
        timestamp = event["headers"].get("x-signature-timestamp")

        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{raw_body}".encode(), bytes.fromhex(signature))
    except BadSignatureError as e:
        logger.info(
            json.dumps(
                {"type": "INVALID_REQUEST_SIGNATURE", "exception": str(e)},
                ensure_ascii=False,
            )
        )
        return {"statusCode": 401, "body": "Invalid request signature"}

    # ping pong
    body = json.loads(raw_body)
    logging.info(
        json.dumps({"type": "REQUEST_BODY", "body": raw_body}, ensure_ascii=False)
    )

    if body.get("type") == TYPE.PING:
        return {"statusCode": 200, "body": json.dumps({"type": 1}, ensure_ascii=False)}

    # 슬래시 명령어 지원 종료 (from 2024.07.06)
    res = {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "embeds": [
                {
                    "title": "웹 대시보드에서 알림 관리하기",
                    "description": "알림 추가, 수정, 삭제 등 모든 관리는 **웹 대시보드**에서 간편하게 가능합니다.\n\n아래 버튼을 눌러 대시보드로 이동해 보세요!",
                    "color": 0x02E895,
                    "footer": {"text": "chzzk.junah.dev"},
                }
            ],
            "components": [
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.BUTTON,
                            "style": BUTTON_STYLE.LINK,
                            "label": "웹 대시보드 바로가기",
                            "url": "https://chzzk.junah.dev",
                        }
                    ],
                }
            ],
        },
    }
    return {"statusCode": 200, "body": json.dumps(res, ensure_ascii=False)}
