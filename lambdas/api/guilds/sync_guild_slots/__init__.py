import json
import logging

import boto3
from shared import middleware
from shared.event import get_path_param
from shared.exceptions import BadRequestError
from shared.notification_dispatcher import query_guild_items
from shared.slots import SlotUsage, count_notifications, count_slot_usage
from shared.utils import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = "chzzk-bot-db"
DEFAULT_MAX_LIMIT = 5

dynamodb = boto3.client("dynamodb")


def set_current_count(guild_id: str, count: int) -> None:
    guild_pk = f"GUILD#{guild_id}"
    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"PK": {"S": guild_pk}, "SK": {"S": guild_pk}},
        UpdateExpression=(
            "SET current_count = :count, "
            "guild_id = if_not_exists(guild_id, :guild_id), "
            "#type = if_not_exists(#type, :type)"
        ),
        ExpressionAttributeNames={"#type": "type"},
        ExpressionAttributeValues={
            ":count": {"N": str(count)},
            ":guild_id": {"S": guild_id},
            ":type": {"S": "GUILD"},
        },
    )


@middleware(require_guild_admin=True)
def handler(event, _context):
    guild_id = get_path_param(event, "guild_id")
    if not guild_id:
        raise BadRequestError()

    items = query_guild_items(guild_id)
    usage = count_slot_usage(guild_id, items) or SlotUsage(
        noti_count=count_notifications(items),
        current_count=0,
        max_limit=DEFAULT_MAX_LIMIT,
    )

    logger.info(
        json.dumps(
            {
                "type": "SYNC_GUILD_SLOTS",
                "guild_id": guild_id,
                "noti_count": usage.noti_count,
                "previous_count": usage.current_count,
                "max_limit": usage.max_limit,
            }
        )
    )

    if not usage.in_sync:
        set_current_count(guild_id, usage.noti_count)

    return build_response(
        200,
        data={
            "current_count": usage.noti_count,
            "previous_count": usage.current_count,
            "max_limit": usage.max_limit,
        },
    )
