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
    custom_message = body.get("custom_message", "")

    disable_embed = body.get("disable_embed", False)
    disable_button = body.get("disable_button", False)
    disable_notification = body.get("disable_notification", False)

    if not all([chzzk_id, channel_id, custom_message]):
        raise BadRequestError()

    try:
        dynamodb.update_item(
            TableName="chzzk-bot-db",
            Key={
                "PK": {"S": f"CHZZK#{chzzk_id}"},
                "SK": {"S": f"NOTI#{channel_id}"},
            },
            UpdateExpression="SET custom_message = :cm, disable_embed = :de, disable_button = :db, disable_notification = :dn",
            ConditionExpression="guild_id = :gid",
            ExpressionAttributeValues={
                ":cm": {"S": custom_message},
                ":de": {"BOOL": disable_embed},
                ":db": {"BOOL": disable_button},
                ":dn": {"BOOL": disable_notification},
                ":gid": {"S": guild_id},
            },
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "body": json.dumps(
                    {"message": "알림 설정을 찾을 수 없거나 권한이 없습니다."}
                ),
            }

        logger.error(
            json.dumps(
                {
                    "type": "UPDATE_NOTIFICATION_ERROR",
                    "chzzk_id": chzzk_id,
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "error": str(e),
                }
            )
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "알림 설정 업데이트 중 오류가 발생했습니다."}),
        }

    return {
        "statusCode": 204,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }
