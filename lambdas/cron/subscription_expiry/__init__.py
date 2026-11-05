import json
import logging
import os
from datetime import UTC, datetime

import boto3
from shared.discord.utils import send_message
from shared.notification_dispatcher import deactivate_subscription_for_guild
from shared.utils import to_kst_string

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_SUBSCRIPTION_EXPIRY_REPORT_CHANNEL_ID = os.environ.get(
    "DISCORD_SUBSCRIPTION_EXPIRY_REPORT_CHANNEL_ID"
)
DISCORD_SUBSCRIPTION_EXPIRY_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_SUBSCRIPTION_EXPIRY_ERROR_CHANNEL_ID"
)

TABLE_NAME = "chzzk-bot-db"
INDEX_NAME = "GSI-Type-ExpiresAt"
DEFAULT_MAX_LIMIT = 5
SLOT_PRODUCT_TYPES = ("SLOT_5", "SLOT_10")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client("dynamodb")


# 하루에 한 번만 실행되므로 만료 후 최대 하루 동안은 구독 기능이 유지된다.
def handler(_event, _context):
    now = datetime.now(UTC).isoformat()
    result = {"expired": [], "skipped": [], "failed": []}
    report_lines = []
    error_lines = []

    try:
        subscriptions = query_expired_subscriptions(now)
    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "SUBSCRIPTION_EXPIRY_QUERY_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        send_error_alert([f"만료된 구독 조회 실패: `{e}`"])
        raise

    for subscription in subscriptions:
        guild_id = subscription["guild_id"]["S"]
        expires_at = subscription["expires_at"]["S"]
        try:
            max_limit = restored_max_limit(query_orders(guild_id))
            expire_subscription(guild_id, expires_at, max_limit)
        except dynamodb.exceptions.TransactionCanceledException as e:
            # 조회 이후 갱신되었거나 GUILD 아이템이 없는 경우
            reasons = [r.get("Code") for r in e.response.get("CancellationReasons", [])]
            logger.warning(
                json.dumps(
                    {
                        "type": "SUBSCRIPTION_EXPIRY_SKIPPED",
                        "guild_id": guild_id,
                        "reasons": reasons,
                    },
                    ensure_ascii=False,
                )
            )
            result["skipped"].append(guild_id)
            report_lines.append(f"⏭️ `{guild_id}` 건너뜀 ({', '.join(reasons)})")
            continue
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "SUBSCRIPTION_EXPIRY_ERROR",
                        "guild_id": guild_id,
                        "error": str(e),
                    },
                    ensure_ascii=False,
                )
            )
            result["failed"].append(guild_id)
            error_lines.append(f"`{guild_id}` 만료 처리 실패: `{e}`")
            continue

        try:
            deactivate_subscription_for_guild(guild_id)
        except Exception as e:
            # 구독은 이미 EXPIRED라 다음 실행에서 다시 처리되지 않으므로 수동 확인이 필요하다.
            logger.error(
                json.dumps(
                    {
                        "type": "SUBSCRIPTION_DEACTIVATE_NOTI_ERROR",
                        "guild_id": guild_id,
                        "error": str(e),
                    },
                    ensure_ascii=False,
                )
            )
            result["failed"].append(guild_id)
            error_lines.append(
                f"`{guild_id}` 구독은 만료됐지만 알림 플래그 해제 실패 (수동 확인 필요): `{e}`"
            )
            continue

        logger.info(
            json.dumps(
                {
                    "type": "SUBSCRIPTION_EXPIRED",
                    "guild_id": guild_id,
                    "expires_at": expires_at,
                    "max_limit": max_limit,
                },
                ensure_ascii=False,
            )
        )
        result["expired"].append(guild_id)
        report_lines.append(
            f"✅ `{guild_id}` 만료 ({to_kst_string(expires_at)} KST), 슬롯 {max_limit}개로 복원"
        )

    logger.info(
        json.dumps({"type": "SUBSCRIPTION_EXPIRY_RESULT", **result}, ensure_ascii=False)
    )
    if report_lines:
        send_report(report_lines)
    if error_lines:
        send_error_alert(error_lines)
    return result


def send_report(lines: list[str]) -> None:
    _send_embed(
        DISCORD_SUBSCRIPTION_EXPIRY_REPORT_CHANNEL_ID,
        {
            "title": "SUBSCRIPTION_EXPIRY_REPORT",
            "description": _join_lines(lines),
            "color": 0x3498DB,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def send_error_alert(lines: list[str]) -> None:
    _send_embed(
        DISCORD_SUBSCRIPTION_EXPIRY_ERROR_CHANNEL_ID,
        {
            "title": "SUBSCRIPTION_EXPIRY_ERROR",
            "description": _join_lines(lines),
            "color": 0xFF0000,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


def _join_lines(lines: list[str]) -> str:
    # 디스코드 임베드 description은 최대 4096자
    return "\n".join(lines)[:4096]


def _send_embed(channel_id: str | None, embed: dict) -> None:
    if not channel_id:
        return
    res = send_message(
        channel_id=channel_id, data={"embeds": [embed]}, token=ADMIN_DISCORD_TOKEN
    )
    if res.status_code not in (200, 201):
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_MESSAGE_SEND_ERROR",
                    "channel_id": channel_id,
                    "status_code": res.status_code,
                    "text": res.text[:1000],
                },
                ensure_ascii=False,
            )
        )


def restored_max_limit(orders: list[dict]) -> int:
    """구독 전 한도인 기본 슬롯 + 단일 구매로 추가한 슬롯 합계를 계산합니다."""
    added = 0
    for order in orders:
        if order.get("product_type", {}).get("S") not in SLOT_PRODUCT_TYPES:
            continue
        if order.get("payment_status", {}).get("S") != "SUCCESS":
            continue
        slot_info = order.get("slot_info", {}).get("M", {})
        added += int(slot_info.get("added_slot", {}).get("N", "0"))
    return DEFAULT_MAX_LIMIT + added


def query_expired_subscriptions(now: str) -> list[dict]:
    return _query_all(
        TableName=TABLE_NAME,
        IndexName=INDEX_NAME,
        KeyConditionExpression="#type = :type AND expires_at <= :now",
        FilterExpression="#status = :active",
        ExpressionAttributeNames={"#type": "type", "#status": "status"},
        ExpressionAttributeValues={
            ":type": {"S": "SUBSCRIPTION"},
            ":now": {"S": now},
            ":active": {"S": "ACTIVE"},
        },
    )


def query_orders(guild_id: str) -> list[dict]:
    return _query_all(
        TableName=TABLE_NAME,
        KeyConditionExpression="PK = :pk AND begins_with(SK, :order)",
        ExpressionAttributeValues={
            ":pk": {"S": f"GUILD#{guild_id}"},
            ":order": {"S": "ORDER#"},
        },
    )


def expire_subscription(guild_id: str, expires_at: str, max_limit: int) -> None:
    guild_pk = f"GUILD#{guild_id}"
    dynamodb.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {"PK": {"S": guild_pk}, "SK": {"S": "SUB#CURRENT"}},
                    "UpdateExpression": "SET #status = :expired",
                    "ConditionExpression": "#status = :active AND expires_at = :expires_at",
                    "ExpressionAttributeNames": {"#status": "status"},
                    "ExpressionAttributeValues": {
                        ":expired": {"S": "EXPIRED"},
                        ":active": {"S": "ACTIVE"},
                        ":expires_at": {"S": expires_at},
                    },
                }
            },
            {
                "Update": {
                    "TableName": TABLE_NAME,
                    "Key": {"PK": {"S": guild_pk}, "SK": {"S": guild_pk}},
                    "UpdateExpression": "SET max_limit = :max_limit",
                    "ConditionExpression": "attribute_exists(PK)",
                    "ExpressionAttributeValues": {":max_limit": {"N": str(max_limit)}},
                }
            },
        ]
    )


def _query_all(**query_args) -> list[dict]:
    items = []
    while True:
        response = dynamodb.query(**query_args)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            return items
        query_args["ExclusiveStartKey"] = last_key
