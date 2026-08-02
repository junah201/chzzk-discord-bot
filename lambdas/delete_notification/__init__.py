import json
import logging

import boto3
from botocore.exceptions import ClientError

from shared import middleware
from shared.exceptions import BadRequestError
from shared.utils import build_response

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id")
    guild_id = body.get("guild_id")
    channel_id = body.get("channel_id")

    if not all([chzzk_id, guild_id, channel_id]):
        raise BadRequestError()

    try:
        # 알림 삭제
        dynamodb.delete_item(
            TableName="chzzk-bot-db",
            Key={
                "PK": {"S": f"CHZZK#{chzzk_id}"},
                "SK": {"S": f"NOTI#{channel_id}"},
            },
            ConditionExpression="guild_id = :guild_id",
            ExpressionAttributeValues={
                ":guild_id": {"S": guild_id},
            },
        )

        # 서버 알림 개수 감소
        table.update_item(
            Key={
                "PK": f"GUILD#{guild_id}",
                "SK": f"GUILD#{guild_id}",
            },
            UpdateExpression="SET current_count = if_not_exists(current_count, :one) - :dec",
            ConditionExpression="current_count > :zero",
            ExpressionAttributeValues={
                ":dec": 1,
                ":one": 1,
                ":zero": 0,
            },
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return build_response(404, "알림을 찾을 수 없거나 권한이 없습니다.")

        logger.error(
            json.dumps(
                {
                    "type": "DELETE_NOTIFICATION_ERROR",
                    "chzzk_id": chzzk_id,
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "error": str(e),
                }
            )
        )
        return build_response(500, "서버 오류가 발생했습니다.")

    return build_response(204)
