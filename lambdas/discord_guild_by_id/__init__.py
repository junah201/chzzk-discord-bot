import json
import logging
import os

import requests

from shared import middleware
from shared.utils import pick

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


@middleware(logger, admin_check=True)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    if not guild_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "guild_id is required"}),
        }

    res = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        },
        params={
            "with_counts": "true"
        },
    )

    if res.status_code == 404:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "해당 서버를 찾을 수 없습니다."}),
        }

    data = res.json()
    logger.info(
        json.dumps(
            {
                "type": "GET_GUILD_BY_ID",
                "guild_id": guild_id,
                "status_code": res.status_code,
                "response": res.text
            }
        )
    )

    if res.status_code == 403:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "봇이 해당 서버에 속해있지 않습니다."}),
        }

    if res.status_code == 401:
        return {
            "statusCode": 403,
            "body": json.dumps({"message": "봇 토큰이 유효하지 않습니다."}),
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

    ALLOWED_KEYS = {'id', 'name', 'icon',
                    "description", 'approximate_member_count'}
    return {
        "statusCode": 200,
        "body": json.dumps(
            pick(data, ALLOWED_KEYS)
        )
    }
