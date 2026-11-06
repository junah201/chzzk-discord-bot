import json
import logging

import boto3
from botocore.exceptions import ClientError
from shared import middleware
from shared.exceptions import BadRequestError, NotificationNotFoundError
from shared.utils import build_response

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id")
    guild_id = body.get("guild_id")
    channel_id = body.get("channel_id")

    if not all([chzzk_id, guild_id, channel_id]):
        raise BadRequestError()

    try:
        # 알림 삭제와 서버 알림 개수 감소를 하나의 트랜잭션으로 처리
        dynamodb.transact_write_items(
            TransactItems=[
                {
                    "Delete": {
                        "TableName": "chzzk-bot-db",
                        "Key": {
                            "PK": {"S": f"CHZZK#{chzzk_id}"},
                            "SK": {"S": f"NOTI#{channel_id}"},
                        },
                        "ConditionExpression": "guild_id = :guild_id",
                        "ExpressionAttributeValues": {
                            ":guild_id": {"S": guild_id},
                        },
                    }
                },
                {
                    "Update": {
                        "TableName": "chzzk-bot-db",
                        "Key": {
                            "PK": {"S": f"GUILD#{guild_id}"},
                            "SK": {"S": f"GUILD#{guild_id}"},
                        },
                        "UpdateExpression": "SET current_count = if_not_exists(current_count, :one) - :dec",
                        "ConditionExpression": "current_count > :zero",
                        "ExpressionAttributeValues": {
                            ":dec": {"N": "1"},
                            ":one": {"N": "1"},
                            ":zero": {"N": "0"},
                        },
                    }
                },
            ]
        )
        logger.info(
            json.dumps(
                {
                    "type": "DELETE_NOTIFICATION_SUCCESS",
                    "chzzk_id": chzzk_id,
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                },
                ensure_ascii=False,
            )
        )

    except ClientError as e:
        if e.response["Error"]["Code"] == "TransactionCanceledException" and any(
            reason.get("Code") == "ConditionalCheckFailed"
            for reason in e.response.get("CancellationReasons", [])
        ):
            raise NotificationNotFoundError() from e

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
