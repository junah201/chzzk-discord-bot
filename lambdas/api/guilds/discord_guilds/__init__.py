import json
import logging

import boto3
from shared import middleware
from shared.discord.utils import get_admin_guilds
from shared.exceptions import (
    DiscordApiUnavailableError,
    RateLimitError,
    UnauthorizedError,
)
from shared.utils import build_response, pick

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_resource = boto3.resource("dynamodb")
dynamodb_client = boto3.client("dynamodb")
table_name = "chzzk-bot-db"
table = dynamodb_resource.Table(table_name)


@middleware(logger, admin_check=False)
def handler(event, _context):
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    if token is None:
        logger.info(json.dumps({"type": "MISSING_TOKEN"}))
        raise UnauthorizedError()

    result = get_admin_guilds(token, with_counts=True, retry=2)

    if result.guilds is None:
        log_data = {
            "status_code": result.status_code,
            "error_message": result.error_message,
        }
        if result.status_code == 429:
            logger.info(json.dumps({"type": "RATE_LIMITED", **log_data}))
            raise RateLimitError(retry_after=result.retry_after)

        logger.error(json.dumps({"type": "GET_ADMIN_GUILDS_FAILED", **log_data}))
        raise DiscordApiUnavailableError()

    ALLOWED_KEYS = {"id", "name", "icon", "approximate_member_count"}
    admin_guilds = [pick(guild, ALLOWED_KEYS) for guild in result.guilds]

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
