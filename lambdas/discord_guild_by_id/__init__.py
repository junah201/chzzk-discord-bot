import json
import logging
import os

import boto3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Timeout
from urllib3.util.retry import Retry

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

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False,
)
adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
session.mount("https://", adapter)
session.headers.update({"Authorization": f"Bot {DISCORD_TOKEN}"})


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

    try:
        res = session.get(
            f"https://api.discord.com/api/v10/guilds/{guild_id}",
            params={"with_counts": "true"},
            timeout=Timeout(connect=3.05, read=5.0),
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_CONNECTION_FAILURE",
                    "guild_id": guild_id,
                    "error": str(e),
                }
            )
        )
        # 네트워크/DNS 단절 시 500 에러 처리
        raise DiscordApiError(None)

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

    if res.status_code == 404:
        raise ServerNotFoundError()

    if res.status_code == 403:
        raise BotNotJoinedError()

    if res.status_code != 200:
        raise DiscordApiError(res)

    # 기본 디스코드 서버 정보 필터링
    ALLOWED_KEYS = {"id", "name", "icon", "description", "approximate_member_count"}
    guild_data = pick(res.json(), ALLOWED_KEYS)

    # DynamoDB 조회
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
