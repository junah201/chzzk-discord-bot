import json
import logging
import re
from datetime import UTC, datetime
from typing import Literal

import boto3
import requests

from shared.discord.utils import (
    DISCORD_API_BASE_URL,
    DISCORD_API_TIMEOUT_SEC,
    network_error_response,
    send_message,
    session,
)
from shared.exceptions import (
    BadRequestError,
    DiscordApiUnavailableError,
    RateLimitError,
)

logger = logging.getLogger()

_DISCORD_WEBHOOK_URL = re.compile(
    r"^https://(?:discord(?:app)?\.com)/api/webhooks/(\d+)/([\w-]+)$"
)
# 토큰으로 실행할 수 있는 일반(Incoming) 웹훅
_INCOMING_WEBHOOK_TYPE = 1
_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_EMBED_COLOR = 0x02E895
dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")


def is_valid_webhook_url(webhook_url: str) -> bool:
    return bool(_DISCORD_WEBHOOK_URL.fullmatch(webhook_url))


def verify_webhook_guild(webhook_url: str, guild_id: str) -> None:
    """웹훅이 존재하고 guild_id 서버의 일반 웹훅인지 디스코드에 조회해서 확인합니다.
    조건에 맞지 않으면 BadRequestError, rate limit이면 RateLimitError,
    네트워크 오류나 5xx면 DiscordApiUnavailableError를 던집니다.
    webhook_url은 is_valid_webhook_url을 통과한 값이어야 합니다.
    """
    webhook_id, webhook_token = _DISCORD_WEBHOOK_URL.fullmatch(webhook_url).groups()
    # 웹훅 토큰이 로그에 남지 않도록 webhook_id만 기록한다.
    log_context = {"guild_id": str(guild_id), "webhook_id": webhook_id}
    try:
        res = session.get(
            f"{DISCORD_API_BASE_URL}/webhooks/{webhook_id}/{webhook_token}",
            timeout=DISCORD_API_TIMEOUT_SEC,
        )
    except requests.RequestException as error:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_GET_WEBHOOK_REQUEST_ERROR",
                    **log_context,
                    "error": str(error),
                },
                ensure_ascii=False,
            )
        )
        raise DiscordApiUnavailableError() from error

    if res.status_code == 429:
        try:
            retry_after = float(res.json()["retry_after"])
        except Exception:
            retry_after = 0
        raise RateLimitError(retry_after)
    if res.status_code in (401, 404):
        raise BadRequestError(
            "디스코드 웹훅을 찾을 수 없습니다. 웹훅이 삭제되지 않았는지, URL을 정확히 복사했는지 확인해주세요."
        )
    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_GET_WEBHOOK_HTTP_ERROR",
                    **log_context,
                    "status_code": res.status_code,
                    "text": res.text[:1000],
                },
                ensure_ascii=False,
            )
        )
        raise DiscordApiUnavailableError()

    webhook = res.json()
    if webhook.get("type") != _INCOMING_WEBHOOK_TYPE:
        raise BadRequestError("유효한 디스코드 웹훅 URL을 입력해주세요.")
    if webhook.get("guild_id") != str(guild_id):
        logger.warning(
            json.dumps(
                {
                    "type": "DISCORD_WEBHOOK_GUILD_MISMATCH",
                    **log_context,
                    "webhook_guild_id": webhook.get("guild_id"),
                },
                ensure_ascii=False,
            )
        )
        raise BadRequestError(
            "다른 디스코드 서버의 웹훅입니다. 알림을 등록하려는 서버에서 만든 웹훅을 입력해주세요."
        )


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


def get_embed_fields(chzzk: dict, notification_item: dict) -> list[dict]:
    """방송 알림 임베드의 필드(카테고리, 태그)를 만듭니다.
    태그는 disable_tag가 없으면 표시하며, 방송에 태그가 없으면 필드를 생략합니다.
    """
    fields = [{"name": "카테고리", "value": chzzk["liveCategoryValue"]}]

    disable_tag = notification_item.get("disable_tag", {}).get("BOOL", False)
    tags = [tag for tag in chzzk.get("tags") or [] if tag]
    if not disable_tag and tags:
        # 디스코드 임베드 필드 값은 최대 1024자
        value = " ".join(f"`{tag}`" for tag in tags)[:1024]
        fields.append({"name": "태그", "value": value})

    return fields


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
        return session.post(
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
        return network_error_response(error)
