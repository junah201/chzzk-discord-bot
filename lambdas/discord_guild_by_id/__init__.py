import json
import logging
import os

import requests

from shared import middleware
from shared.exceptions import (
    BadRequestError,
    BotNotJoinedError,
    DiscordApiError,
    ServerNotFoundError,
)
from shared.utils import pick

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


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
        f"https://discord.com/api/v10/guilds/{guild_id}",
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

    ALLOWED_KEYS = {"id", "name", "icon", "description", "approximate_member_count"}
    return {"statusCode": 200, "body": json.dumps(pick(data, ALLOWED_KEYS))}
