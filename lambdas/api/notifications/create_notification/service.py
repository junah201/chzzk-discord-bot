import json
import logging

import boto3
from shared.exceptions import BadRequestError
from shared.notification_dispatcher import is_guild_subscription_active

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")

logger = logging.getLogger()


def check_guild_limit(guild_id: str) -> None:
    """서버의 알림 등록 제한 검증. 슬롯이 없으면 BadRequestError를 던진다."""
    guild_res = table.get_item(
        Key={"PK": f"GUILD#{guild_id}", "SK": f"GUILD#{guild_id}"}
    )
    guild_item = guild_res.get("Item")

    max_limit = int(guild_item.get("max_limit", 5)) if guild_item else 5
    current_count = int(guild_item.get("current_count", 0)) if guild_item else 0

    if current_count >= max_limit:
        raise BadRequestError(
            f"알림 슬롯 {max_limit}개를 모두 사용했습니다.",
            code="NOTIFICATION_LIMIT_REACHED",
            details={"max_limit": max_limit, "current_count": current_count},
        )


def is_chzzk_registered(chzzk_id: str) -> bool:
    """치지직 채널 정보 등록 여부 확인"""
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"CHZZK#{chzzk_id}"},
        },
    )
    return bool(res.get("Items", []))


def register_chzzk_channel(chzzk_id: str, chzzk_data: dict, index: int) -> bool:
    """치지직 채널 정보 DB 저장"""
    res = dynamodb.put_item(
        TableName="chzzk-bot-db",
        Item={
            "PK": {"S": f"CHZZK#{chzzk_id}"},
            "SK": {"S": f"CHZZK#{chzzk_id}"},
            "lastLiveId": {"N": f"{chzzk_data['liveId']}"},
            "lastLiveTitle": {"S": chzzk_data["liveTitle"]},
            "channelId": {"S": chzzk_data["channel"]["channelId"]},
            "channelName": {"S": chzzk_data["channel"]["channelName"]},
            "channelImageUrl": {"S": chzzk_data["channel"]["channelImageUrl"] or ""},
            "type": {"S": "CHZZK"},
            "index": {"N": f"{index}"},
        },
    )
    return res["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_naver_account(index: int) -> dict | None:
    """네이버 세션 쿠키 정보 조회"""
    res = table.get_item(Key={"PK": "NAVER#ACCOUNTS", "SK": f"NAVER#{index}"})
    return res.get("Item")


def is_notification_exists(chzzk_id: str, channel_id: str, guild_id: str) -> bool:
    """동일 서버/채널에 이미 등록된 알림인지 확인"""
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        FilterExpression="guild_id = :guild_id",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"NOTI#{channel_id}"},
            ":guild_id": {"S": guild_id},
        },
    )
    return bool(res.get("Items", []))


def save_notification_and_increment_counter(
    guild_id: str,
    channel_id: str,
    channel_data: dict,
    chzzk_id: str,
    chzzk_data: dict,
    body: dict,
):
    """NOTI 아이템 저장과 GUILD current_count 증가(+1)를 하나의 트랜잭션으로 처리합니다.
    GUILD가 없으면 같은 트랜잭션에서 기본값(max_limit 5)으로 만들고, 있으면 기존 값을 유지합니다.
    """
    item = {
        "PK": {"S": f"CHZZK#{chzzk_id}"},
        "SK": {"S": f"NOTI#{channel_id}"},
        "chzzk_id": {"S": str(chzzk_id)},
        "chzzk_name": {"S": chzzk_data["channel"]["channelName"]},
        "chzzk_image_url": {"S": chzzk_data["channel"]["channelImageUrl"] or ""},
        "channel_id": {"S": str(channel_id)},
        "channel_name": {"S": channel_data.get("name", "")},
        "guild_id": {"S": guild_id},
        "custom_message": {"S": body.get("custom_message", "")},
        "type": {"S": "NOTI"},
        "disable_embed": {"BOOL": body.get("disable_embed", False)},
        "disable_button": {"BOOL": body.get("disable_button", False)},
        "disable_tag": {"BOOL": body.get("disable_tag", False)},
        "disable_notification": {"BOOL": body.get("disable_notification", False)},
        "index": {"N": "-1"},
    }
    webhook_url = body.get("webhook_url", "").strip()
    embed_color = body.get("embed_color", "").strip()
    auto_crosspost = body.get("auto_crosspost", False)

    if webhook_url or embed_color or auto_crosspost:
        is_subscription_active = is_guild_subscription_active(guild_id)
        item["is_subscription_active"] = {"BOOL": is_subscription_active}
    if webhook_url:
        item["webhook_url"] = {"S": webhook_url}
    if embed_color:
        item["embed_color"] = {"S": embed_color}
    if auto_crosspost:
        item["auto_crosspost"] = {"BOOL": True}

    transaction_items = [
        {
            "Put": {
                "TableName": "chzzk-bot-db",
                "Item": item,
                "ConditionExpression": "attribute_not_exists(SK)",
            }
        },
        {
            "Update": {
                "TableName": "chzzk-bot-db",
                "Key": {
                    "PK": {"S": f"GUILD#{guild_id}"},
                    "SK": {"S": f"GUILD#{guild_id}"},
                },
                # 동시에 처음 등록해도 GUILD를 덮어쓰지 않도록 기본값은 없을 때만 넣는다.
                "UpdateExpression": (
                    "SET #type = if_not_exists(#type, :type), "
                    "guild_id = if_not_exists(guild_id, :guild_id), "
                    "max_limit = if_not_exists(max_limit, :max_limit) "
                    "ADD current_count :inc"
                ),
                "ExpressionAttributeNames": {"#type": "type"},
                "ExpressionAttributeValues": {
                    ":inc": {"N": "1"},
                    ":type": {"S": "GUILD"},
                    ":guild_id": {"S": guild_id},
                    ":max_limit": {"N": "5"},
                },
            }
        },
    ]

    try:
        dynamodb.transact_write_items(TransactItems=transaction_items)
        logger.info(
            json.dumps(
                {
                    "type": "SAVE_NOTIFICATION_SUCCESS",
                    "chzzk_id": chzzk_id,
                    "channel_id": channel_id,
                    "guild_id": guild_id,
                },
                ensure_ascii=False,
            )
        )
    except dynamodb.exceptions.TransactionCanceledException as e:
        logger.error(
            json.dumps(
                {"type": "SAVE_NOTIFICATION_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        raise
