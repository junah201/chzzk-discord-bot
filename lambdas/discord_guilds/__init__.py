import json
import logging
import time

import boto3
import requests

from shared import middleware
from shared.exceptions import DiscordApiError, RateLimitError, UnauthorizedError
from shared.utils import build_response, pick

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_resource = boto3.resource("dynamodb")
dynamodb_client = boto3.client("dynamodb")
table_name = "chzzk-bot-db"
table = dynamodb_resource.Table(table_name)


@middleware(logger, admin_check=False)
def handler(event, context):
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    if token is None:
        logger.info(json.dumps({"type": "MISSING_TOKEN"}))
        raise UnauthorizedError()

    retry = 2
    for _retry_count in range(1, retry + 1):
        res = requests.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": token},
            params={"with_counts": "true"},
        )

        if res.status_code == 429:
            data = res.json()
            time.sleep(data["retry_after"] + 0.1)
            continue
        break

    if res.status_code == 429:
        logger.info(
            json.dumps(
                {
                    "type": "RATE_LIMITED",
                    "status_code": res.status_code,
                    "response": res.text,
                }
            )
        )
        raise RateLimitError(retry_after=data["retry_after"])

    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "INVALID_TOKEN",
                    "status_code": res.status_code,
                    "response": res.text,
                }
            )
        )
        raise DiscordApiError(res)

    data = res.json()

    # 관리자 권한을 가진 서버만 필터링
    ALLOWED_KEYS = {"id", "name", "icon", "description", "approximate_member_count"}
    admin_guilds = [
        pick(guild, ALLOWED_KEYS)
        for guild in data
        if (guild["permissions"] & 0x8) == 0x8
    ]

    if not admin_guilds:
        return build_response(200, data=[])

    guild_ids = [g["id"] for g in admin_guilds]
    guild_metadata_map = {}

    chunk_size = 100
    for i in range(0, len(guild_ids), chunk_size):
        chunk_ids = guild_ids[i : i + chunk_size]

        keys_to_get = [
            {
                "PK": {"S": f"GUILD#{gid}"},
                "SK": {"S": f"GUILD#{gid}"},
            }
            for gid in chunk_ids
        ]

        response = dynamodb_client.batch_get_item(
            RequestItems={table_name: {"Keys": keys_to_get}}
        )

        responses = response.get("Responses", {}).get(table_name, [])
        for item in responses:
            gid = item.get("guild_id", {}).get("S")
            if gid:
                guild_metadata_map[gid] = {
                    "current_count": int(item.get("current_count", {}).get("N", 0)),
                    "max_limit": int(item.get("max_limit", {}).get("N", 5)),
                }

    guilds_with_info = []
    for g in admin_guilds:
        guild_id = g["id"]
        meta = guild_metadata_map.get(guild_id, {"current_count": 0, "max_limit": 5})

        g["current_count"] = meta["current_count"]
        g["max_limit"] = meta["max_limit"]
        guilds_with_info.append(g)

    return build_response(200, data=guilds_with_info)
