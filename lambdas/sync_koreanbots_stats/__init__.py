import json
import logging
import os

import requests

from shared.discord.utils import send_message

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
KOREANBOTS_TOKEN = os.environ.get("KOREANBOTS_TOKEN")
DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID = os.environ.get("DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # 디스코드 API에서 봇 정보 및 서버 수 조회
    try:
        discord_res = requests.get(
            "https://discord.com/api/v10/applications/@me",
            headers={
                "Authorization": f"Bot {DISCORD_TOKEN}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        discord_res.raise_for_status()
        discord_data = discord_res.json()

        bot_id = discord_data.get("id")
        server_count = discord_data.get(
            "bot_approximate_guild_count",
            discord_data.get("approximate_guild_count", 0),
        )

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_GET_GUILD_COUNT_ERROR",
                    "error": str(e),
                    "text": discord_res.text if "discord_res" in locals() else None,
                }
            )
        )
        return {"statusCode": 500, "error": "Failed to fetch discord bot stats"}

    # 한디리 API로 서버 수 업데이트 요청
    try:
        kb_res = requests.post(
            f"https://koreanbots.dev/api/v2/bots/{bot_id}/stats",
            headers={
                "Authorization": KOREANBOTS_TOKEN,
                "Content-Type": "application/json",
            },
            json={"servers": server_count},
            timeout=10,
        )
        kb_res.raise_for_status()

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "KOREANBOTS_UPDATE_STATS_ERROR",
                    "bot_id": bot_id,
                    "servers": server_count,
                    "error": str(e),
                    "status_code": kb_res.status_code if "kb_res" in locals() else None,
                    "text": kb_res.text if "kb_res" in locals() else None,
                }
            )
        )
        send_message(
            channel_id=DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID,
            data={
                "embeds": [
                    {
                        "title": "KOREANBOTS_UPDATE_STATS_ERROR",
                        "description": "한디리 서버 수 업데이트 API 호출에 실패했습니다.",
                        "color": 0xFF0000,
                        "fields": [
                            {"name": "Bot ID", "value": f"`{bot_id}`", "inline": True},
                            {"name": "Servers", "value": f"`{server_count}`", "inline": True},
                            {"name": "Error", "value": f"`{str(e)}`", "inline": False},
                            {
                                "name": "Response Text",
                                "value": f"```{kb_res.text[:500]}```"
                                if "kb_res" in locals()
                                else "`None`",
                                "inline": False,
                            },
                        ],
                    }
                ]
            },
        )
        return {"statusCode": 500, "error": "Failed to update Koreanbots stats"}

    result = {
        "type": "KOREANBOTS_UPDATE_SUCCESS",
        "bot_id": bot_id,
        "servers": server_count,
        "response": kb_res.json() if kb_res.text else {},
    }

    logger.info(json.dumps(result))
    return result


def send_error_alert(title: str, description: str, fields: list):
    if not DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID:
        return

    send_message(
        channel_id=DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID,
        data={
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": 0xFF0000,
                    "fields": fields,
                }
            ]
        },
    )
