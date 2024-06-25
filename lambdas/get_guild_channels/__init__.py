import os
import json
import logging
import requests

from shared import middleware
from shared.discord import CHANNEL_TYPE


logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


@middleware(logger)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    res = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}/channels",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
    )

    # 해당 서버가 존재하지 않거나 접근할 수 없는 경우
    if res.status_code == 404:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "guild not found"}),
        }

    data = res.json()
    logger.info(
        json.dumps(
            {
                "type": "GET_GUILD_CHANNELS",
                "guild_id": guild_id,
                "status_code": res.status_code,
                "response": res.text
            }
        )
    )

    if res.status_code == 403:
        return {
            "statusCode": 403,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "you don't have permission"}),
        }

    if res.status_code == 401:
        return {
            "statusCode": 401,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "token is invalid"}),
        }

    if res.status_code != 200:
        return {
            "statusCode": 400,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "unknown error"}),
        }

    # 채팅 채널 목록을 필터링합니다. (채널이 텍스트 채널 혹은 공지 채널이여야 합니다.)
    channels = [
        channel
        for channel in data
        if channel["type"] in [CHANNEL_TYPE.GUILD_TEXT, CHANNEL_TYPE.GUILD_NEWS]
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(channels)
    }
