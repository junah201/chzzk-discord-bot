import json
import logging
import os

import requests

from shared import middleware
from shared.discord import CHANNEL_TYPE
from shared.exceptions import (
    BotNotJoinedError,
    DiscordApiError,
    ServerNotFoundError,
    UnauthorizedError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


@middleware(logger, admin_check=True)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    res = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}/channels",
        headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
    )

    # 해당 서버가 존재하지 않거나 접근할 수 없는 경우
    if res.status_code == 404:
        raise ServerNotFoundError()

    data = res.json()
    logger.info(
        json.dumps(
            {
                "type": "GET_GUILD_CHANNELS",
                "guild_id": guild_id,
                "status_code": res.status_code,
                "response": res.text,
            }
        )
    )

    if res.status_code == 403:
        raise BotNotJoinedError()

    if res.status_code == 401:
        raise UnauthorizedError()

    if res.status_code != 200:
        raise DiscordApiError(res)

    # 채팅 채널 목록을 필터링합니다. (채널이 텍스트 채널 혹은 공지 채널이여야 합니다.)
    channels = [
        channel
        for channel in data
        if channel["type"] in [CHANNEL_TYPE.GUILD_TEXT, CHANNEL_TYPE.GUILD_NEWS]
    ]

    return {"statusCode": 200, "body": json.dumps(channels)}
