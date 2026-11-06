import json
import logging
import os

from shared import BUTTON_STYLE, COMPONENT_TYPE, TYPE, middleware
from shared.discord.bot import (
    INVALID_SIGNATURE_RESPONSE,
    PONG,
    reply,
    verify_signature,
)
from shared.utils import build_response

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY")
DASHBOARD_URL = "https://chzzk.junah.dev"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 슬래시 명령어 지원 종료 (from 2024.07.06): 모든 명령어에 대시보드 안내로 답합니다.
DASHBOARD_GUIDE = reply(
    embeds=[
        {
            "title": "웹 대시보드에서 알림 관리하기",
            "description": "알림 추가, 수정, 삭제 등 모든 관리는 **웹 대시보드**에서 간편하게 가능합니다.\n\n아래 버튼을 눌러 대시보드로 이동해 보세요!",
            "color": 0x02E895,
            "footer": {"text": "chzzk.junah.dev"},
        }
    ],
    components=[
        {
            "type": COMPONENT_TYPE.ACTION_ROW,
            "components": [
                {
                    "type": COMPONENT_TYPE.BUTTON,
                    "style": BUTTON_STYLE.LINK,
                    "label": "웹 대시보드 바로가기",
                    "url": DASHBOARD_URL,
                }
            ],
        }
    ],
)


@middleware(logger)
def handler(event, _context):
    raw_body = event["body"]
    if not verify_signature(DISCORD_PUBLIC_KEY, event["headers"], raw_body):
        return INVALID_SIGNATURE_RESPONSE

    body = json.loads(raw_body)
    logger.info(
        json.dumps({"type": "REQUEST_BODY", "body": raw_body}, ensure_ascii=False)
    )

    if body.get("type") == TYPE.PING:
        return build_response(200, data=PONG)

    return build_response(200, data=DASHBOARD_GUIDE)
