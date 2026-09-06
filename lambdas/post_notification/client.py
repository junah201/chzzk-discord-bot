import json
import logging
import os

import requests
from user_agent import generate_user_agent

from shared.discord.utils import send_message

DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID"
)
logger = logging.getLogger()


def follow_chzzk_channel(chzzk_id: str, index: int, naver_item: dict) -> bool:
    """치지직 채널 팔로우 요청 수행 및 에러 로그 처리"""
    nid_aut = naver_item.get("NID_AUT")
    nid_ses = naver_item.get("NID_SES")

    res = requests.post(
        f"https://api.chzzk.naver.com/service/v1/channels/{chzzk_id}/follow",
        headers={
            "User-Agent": generate_user_agent(os="win", device_type="desktop"),
            "Cookie": f"NID_AUT={nid_aut}; NID_SES={nid_ses}",
        },
        timeout=2,
    )

    if res.status_code != 200:
        _log_and_send_follow_error(chzzk_id, index, res)
        return False

    logger.info(
        json.dumps(
            {"type": "CHZZK_FOLLOW_SUCCESS", "channel_id": chzzk_id},
            ensure_ascii=False,
        )
    )
    return True


def _log_and_send_follow_error(chzzk_id: str, index: int, res: requests.Response):
    """팔로우 실패시 로그 기록 및 디스코드 알림 채널 전송"""
    logger.error(
        json.dumps(
            {
                "type": "CHZZK_FOLLOW_ERROR",
                "chzzk_id": chzzk_id,
                "index": index,
                "status_code": res.status_code,
                "text": res.text,
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
                    "description": f"Failed to follow CHZZK channel. Status code: {res.status_code}",
                    "color": 0xFF0000,
                    "fields": [
                        {"name": "chzzk_id", "value": str(chzzk_id)},
                        {"name": "text", "value": res.text},
                        {"name": "index", "value": str(index)},
                    ],
                }
            ]
        },
    )
