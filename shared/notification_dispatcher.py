import json
import logging
import re
from datetime import UTC, datetime
from typing import Literal

import boto3
import requests

from shared.discord.utils import send_message

logger = logging.getLogger()

_DISCORD_WEBHOOK_URL = re.compile(
    r"^https://(?:discord(?:app)?\.com)/api/webhooks/\d+/[\w-]+$"
)
_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_EMBED_COLOR = 0x02E895
dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")


def is_valid_webhook_url(webhook_url: str) -> bool:
    return bool(_DISCORD_WEBHOOK_URL.fullmatch(webhook_url))


def parse_embed_color(embed_color: str) -> int | None:
    """Return a Discord-compatible color integer, or None for an invalid value."""
    value = embed_color.strip()
    if _HEX_COLOR.fullmatch(value):
        return int(value[1:], 16)
    if value.isdecimal():
        color = int(value)
        if 0 <= color <= 0xFFFFFF:
            return color
    return None


def get_embed_color(notification_item: dict) -> int:
    """Use a custom color only while the notification has an active subscription."""
    is_subscription_active = notification_item.get("is_subscription_active", {}).get(
        "BOOL", False
    )
    embed_color = notification_item.get("embed_color", {}).get("S", "")
    if is_subscription_active:
        parsed_color = parse_embed_color(embed_color)
        if parsed_color is not None:
            return parsed_color
    return DEFAULT_EMBED_COLOR


def is_guild_subscription_active(guild_id: str) -> bool:
    """
    특정 길드의 현재 구독 상태(SUB#CURRENT)가 유효한지(ACTIVE 및 만료 전) 확인합니다.
    """
    guild_id_str = str(guild_id)
    guild_pk = f"GUILD#{guild_id_str}"

    try:
        response = table.get_item(Key={"PK": guild_pk, "SK": "SUB#CURRENT"})
        sub_item = response.get("Item")

        if not sub_item:
            return False

        status: Literal["ACTIVE", "EXPIRED", "SUSPENDED"] = sub_item.get("status")
        expires_at_str = sub_item.get("expires_at")

        if status != "ACTIVE":
            return False

        if not expires_at_str:
            logger.warning(
                json.dumps(
                    {
                        "type": "SUBSCRIPTION_EXPIRES_AT_MISSING",
                        "guild_id": guild_id_str,
                    },
                    ensure_ascii=False,
                )
            )
            return False

        now_utc_str = datetime.now(UTC).isoformat()

        return expires_at_str > now_utc_str

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "SUBSCRIPTION_CHECK_ERROR",
                    "guild_id": guild_id_str,
                    "error": str(e),
                },
                ensure_ascii=False,
            )
        )
        return False


def activate_subscription_for_guild(guild_id: str) -> None:
    for item in _query_guild_items(guild_id):
        if item.get("type", {}).get("S") != "NOTI":
            continue
        dynamodb.update_item(
            TableName="chzzk-bot-db",
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression="SET is_subscription_active = :active",
            ExpressionAttributeValues={":active": {"BOOL": True}},
        )


def _query_guild_items(guild_id: str) -> list[dict]:
    items = []
    query_args = {
        "TableName": "chzzk-bot-db",
        "IndexName": "GSI-GuildID-v2",
        "KeyConditionExpression": "guild_id = :guild_id",
        "ExpressionAttributeValues": {":guild_id": {"S": guild_id}},
    }
    while True:
        response = dynamodb.query(**query_args)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            return items
        query_args["ExclusiveStartKey"] = last_key


def send_notification_message(
    *,
    guild_id: str,
    channel_id: str,
    data: dict,
    notification_item: dict,
) -> requests.Response:
    webhook_url = notification_item.get("webhook_url", {}).get("S", "")
    is_subscription_active = notification_item.get("is_subscription_active", {}).get(
        "BOOL", False
    )

    if not is_subscription_active or not webhook_url:
        return send_message(channel_id=channel_id, data=data)

    # 웹훅 메시지 전송 (유료 구독자 전용)
    response = _send_webhook(webhook_url, data)
    if response.status_code not in (200, 204):
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_WEBHOOK_INVALID",
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "status_code": response.status_code,
                    "response_text": response.text,
                },
                ensure_ascii=False,
            )
        )

    return response


def _send_webhook(webhook_url: str, data: dict) -> requests.Response:
    try:
        return requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=5,
        )
    except requests.RequestException as error:
        logger.error(
            json.dumps(
                {"type": "DISCORD_WEBHOOK_REQUEST_ERROR", "error": str(error)},
                ensure_ascii=False,
            )
        )
        response = requests.Response()
        response.status_code = 599
        response._content = str(error).encode()
        return response
