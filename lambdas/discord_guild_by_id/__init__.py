import json
import logging
import os

import boto3
import requests

from shared import middleware
from shared.exceptions import (
    BadRequestError,
    BotNotJoinedError,
    DiscordApiError,
    ServerNotFoundError,
)
from shared.utils import build_response, pick

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("chzzk-bot-db")


@middleware(logger, admin_check=True)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    if not guild_id:
        logger.info(
            json.dumps(
                {
                    "type": "MISSING_GUILD_ID",
                }
            )
        )
        raise BadRequestError()

    res = requests.get(
        f"https://api.discord.com/api/v10/guilds/{guild_id}",
        headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
        params={"with_counts": "true"},
    )

    if res.status_code == 404:
        raise ServerNotFoundError()

    data = res.json()
    logger.info(
        json.dumps(
            {
                "type": "GET_GUILD_BY_ID",
                "guild_id": guild_id,
                "status_code": res.status_code,
                "response": res.text,
            }
        )
    )

    if res.status_code == 403:
        raise BotNotJoinedError()

    if res.status_code != 200:
        raise DiscordApiError(res)

    # 기본 디스코드 서버 정보 필터링
    ALLOWED_KEYS = {"id", "name", "icon", "description", "approximate_member_count"}
    guild_data = pick(data, ALLOWED_KEYS)

    guild_res = table.get_item(
        Key={
            "PK": f"GUILD#{guild_id}",
            "SK": f"GUILD#{guild_id}",
        }
    )
    guild_item = guild_res.get("Item")

    current_count = int(guild_item.get("current_count", 0)) if guild_item else 0
    max_limit = int(guild_item.get("max_limit", 5)) if guild_item else 5

    guild_data["current_count"] = current_count
    guild_data["max_limit"] = max_limit

    return build_response(200, data=guild_data)
