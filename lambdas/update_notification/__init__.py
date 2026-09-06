import json
import logging

import boto3
from botocore.exceptions import ClientError

from shared import middleware
from shared.exceptions import BadRequestError
from shared.utils import build_response

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

    if not all([chzzk_id, guild_id, channel_id]):
        raise BadRequestError()

    try:
        guild_response = dynamodb.get_item(
            TableName="chzzk-bot-db",
            Key={
                "PK": {"S": f"GUILD#{guild_id}"},
                "SK": {"S": f"GUILD#{guild_id}"},
            },
        )

        guild_item = guild_response.get("Item")

        if not guild_item:
            return build_response(
                404,
                "서버 메타데이터를 찾을 수 없습니다. 서버가 삭제되었거나, 알림 설정이 존재하지 않을 수 있습니다. 새로고침 후 다시 시도해주세요. 만약 계속 실패하면 서포트 서버를 통해 관리자에게 문의해주세요.",
            )

        current_count = int(guild_item.get("current_count", {"N": "0"})["N"])
        max_limit = int(guild_item.get("max_limit", {"N": "5"})["N"])

        if current_count > max_limit:
            return build_response(
                400,
                f"현재 서버에 등록된 알림이 제한 개수({max_limit}개)를 초과하여 설정을 수정할 수 없습니다. "
                f"초과된 알림({current_count}/{max_limit})을 정리(삭제)한 후 다시 시도해주세요.",
            )

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
            return build_response(404, "알림 설정을 찾을 수 없거나 권한이 없습니다.")

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
        return build_response(500, "알림 설정 업데이트 중 오류가 발생했습니다.")

    return build_response(204)
