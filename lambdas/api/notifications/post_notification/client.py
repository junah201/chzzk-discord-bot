import json
import logging
import os
from datetime import datetime

from shared.chzzk import follow_chzzk_channel
from shared.discord.utils import send_message

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID"
)
logger = logging.getLogger()


def process_follow(chzzk_id: str, index: int, naver_item: dict):
    nid_aut = naver_item.get("NID_AUT")
    nid_ses = naver_item.get("NID_SES")

    success, status_code, err_message = follow_chzzk_channel(chzzk_id, nid_aut, nid_ses)

    if not success:
        _log_and_send_follow_error(chzzk_id, index, status_code, err_message)
        return False, err_message

    return True, ""


def _log_and_send_follow_error(
    chzzk_id: str, index: int, status_code: int, err_message: str
):
    """팔로우 실패시 로그 기록 및 디스코드 알림 채널 전송"""
    logger.error(
        json.dumps(
            {
                "type": "CHZZK_FOLLOW_ERROR",
                "chzzk_id": chzzk_id,
                "index": index,
                "status_code": status_code,
                "err_message": err_message,
            },
            ensure_ascii=False,
        )
    )
    send_message(
        channel_id=DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID,
        data={
            "embeds": [
                {
                    "title": "CHZZK_FOLLOW_ERROR",
                    "description": "치지직 채널 팔로우 처리에 실패했습니다.",
                    "color": 0xFF0000,
                    "fields": [
                        {"name": "chzzk_id", "value": chzzk_id},
                        {"name": "status_code", "value": str(status_code)},
                        {"name": "err_message", "value": err_message},
                        {"name": "index", "value": str(index)},
                    ],
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        },
        token=ADMIN_DISCORD_TOKEN,
    )
