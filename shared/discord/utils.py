import logging
from typing import Tuple
import requests
import json
import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


def delete_message(channel_id: int, message_id: int):
    res = requests.delete(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
    )
    if res.status_code != 204:
        raise Exception(
            f"Failed to delete message: {res.status_code} {res.text}")


def send_message(channel_id: int, data: dict, token=DISCORD_TOKEN):
    res = requests.post(
        f"https://discord.com/api/v9/channels/{channel_id}/messages",
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )

    return res


def get_channel(channel_id, token=DISCORD_TOKEN) -> dict | None:
    res = requests.get(
        f"https://discord.com/api/v10/channels/{channel_id}",
        headers={
            "Authorization": f"Bot {token}",
        },
    )
    if res.status_code != 200:
        return None

    return res.json()


def is_admin(guild_id: str | int, token: str = None, logger: logging.Logger | None = None) -> Tuple[bool, requests.Response]:
    """
    해당 유저가 관리자 권한을 가진 서버인지 확인합니다.
    """
    res = requests.get(
        "https://discord.com/api/users/@me/guilds",
        headers={
            "Authorization": token
        }
    )
    if res.status_code != 200:
        if logger:
            logger.error(
                json.dumps(
                    {
                        "type": "ADMIN_CHECK_FAILED",
                        "status_code": res.status_code,
                        "response": res.text
                    }
                )
            )
        return False, res

    data = res.json()

    # 관리자권한을 가진 서버만 필터링합니다.
    guilds = [
        guild
        for guild in data
        if (guild["permissions"] & 0x8) == 0x8
    ]

    return str(guild_id) in [guild["id"] for guild in guilds], res
