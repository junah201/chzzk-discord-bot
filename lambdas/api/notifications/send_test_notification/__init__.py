import json
import logging
from datetime import UTC, datetime

import boto3
from shared import get_chzzk, middleware
from shared.event import get_json_body
from shared.exceptions import (
    BadRequestError,
    ChzzkChannelUnavailableError,
    DiscordChannelNotFoundError,
    NotificationNotFoundError,
    SendTestNotificationError,
)
from shared.live_message import build_live_message
from shared.notification_dispatcher import send_notification_message
from shared.utils import build_response

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(require_guild_admin=True)
def handler(event, _context):
    body = get_json_body(event)

    chzzk_id = body.get("chzzk_id", None)
    guild_id = body.get("guild_id", None)
    discord_channel_id = body.get("channel_id", None)

    if not all([chzzk_id, guild_id, discord_channel_id]):
        raise BadRequestError()

    chzzk = get_chzzk(chzzk_id)
    if not chzzk:
        raise ChzzkChannelUnavailableError()

    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="PK = :pk_val AND SK = :sk_val",
        FilterExpression="guild_id = :guild_id",
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"NOTI#{discord_channel_id}"},
            ":guild_id": {"S": guild_id},
        },
    )

    if res["Count"] < 1:
        raise NotificationNotFoundError()

    item = res["Items"][0]

    data = build_live_message(
        chzzk_id,
        chzzk,
        item,
        content="관리자의 요청에 따라 전송된 테스트 알림입니다."
        + "\n\n"
        + item.get("custom_message", {}).get("S", ""),
        now=datetime.now(UTC),
    )

    res = send_notification_message(
        guild_id=guild_id,
        channel_id=discord_channel_id,
        data=data,
        notification_item=item,
    )

    uses_webhook = bool(
        item.get("webhook_url", {}).get("S")
        and item.get("is_subscription_active", {}).get("BOOL", False)
    )

    if res.status_code == 404 and not uses_webhook:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_CHANNEL_NOT_FOUND",
                    "status_code": res.status_code,
                    "response": res.text,
                    "channel_id": discord_channel_id,
                    "chzzk_id": chzzk_id,
                    "data": data,
                },
                ensure_ascii=False,
            )
        )
        raise DiscordChannelNotFoundError()

    if res.status_code not in (200, 204):
        logger.error(
            json.dumps(
                {
                    "type": "SEND_MESSAGE_FAIL",
                    "status_code": res.status_code,
                    "response": res.text,
                    "channel_id": discord_channel_id,
                    "chzzk_id": chzzk_id,
                    "data": data,
                },
                ensure_ascii=False,
            )
        )

        try:
            error_detail = res.json().get("message", res.text)
        except Exception:
            error_detail = res.text

        raise SendTestNotificationError(
            via_webhook=uses_webhook,
            discord_message=error_detail,
        )

    logger.info(
        json.dumps(
            {
                "type": "SEND_MESSAGE_SUCCESS",
                "channel_id": discord_channel_id,
                "chzzk_id": chzzk_id,
                "data": data,
            },
            ensure_ascii=False,
        )
    )
    return build_response(200, "테스트 알림을 성공적으로 전송했습니다.")
