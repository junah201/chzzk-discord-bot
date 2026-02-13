import json
import logging

import boto3
from botocore.exceptions import ClientError

from shared import middleware
from shared.exceptions import BadRequestError

dynamodb = boto3.client("dynamodb")

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
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {"message": "알림을 찾을 수 없거나 권한이 없습니다."}
                ),
            }

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
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "서버 오류가 발생했습니다."}),
        }

    return {
        "statusCode": 204,
    }
