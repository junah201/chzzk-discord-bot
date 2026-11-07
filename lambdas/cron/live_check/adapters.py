import json
import logging
import os
import time
import traceback
from datetime import UTC, datetime

import boto3
import requests
from shared import Following, send_message
from shared.notification_dispatcher import send_notification_message
from user_agent import generate_user_agent

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID"
)

LIVE_STREAMS_SOURCE_URL = os.environ.get("LIVE_STREAMS_SOURCE_URL")
CHZZK_FOLLOWINGS_TIMEOUT_SEC = 10
BATCH_GET_MAX_KEYS = 100
BATCH_GET_MAX_ATTEMPTS = 5
BATCH_GET_BACKOFF_SEC = 0.05
TABLE_NAME = "chzzk-bot-db"

logger = logging.getLogger()

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def get_naver_session(index: int) -> tuple[str, str]:
    res = table.get_item(Key={"PK": "NAVER#ACCOUNTS", "SK": f"NAVER#{index}"})
    naver = res.get("Item")
    return naver.get("NID_AUT"), naver.get("NID_SES")


def fetch_live_streams(NID_AUT: str, NID_SES: str, index: int) -> list[Following]:
    res = requests.get(
        LIVE_STREAMS_SOURCE_URL,
        headers={
            "User-Agent": generate_user_agent(os="win", device_type="desktop"),
            "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}",
        },
        timeout=CHZZK_FOLLOWINGS_TIMEOUT_SEC,
    )

    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "GET_FOLLOWING_ERROR",
                    "status_code": res.status_code,
                    "text": res.text,
                    "index": index,
                },
                ensure_ascii=False,
            )
        )
        send_message(
            channel_id=DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID,
            data={
                "embeds": [
                    {
                        "title": "GET_FOLLOWING_ERROR",
                        "description": f"Failed to fetch live streams. Status code: {res.status_code}",
                        "color": 0xFF0000,
                        "fields": [
                            {"name": "text", "value": res.text},
                            {"name": "index", "value": str(index)},
                        ],
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                ]
            },
            token=ADMIN_DISCORD_TOKEN,
        )
        return []

    content = res.json().get("content") or {}
    following_list = content.get("followingList", [])
    total_count = content.get("totalCount", 0)
    total_live_count = content.get("totalLiveCount", 0)

    logger.info(
        json.dumps(
            {
                "type": "GET_FOLLOWING_SUCCESS",
                "count": len(following_list),
                "index": index,
                "total_count": total_count,
                "total_live_count": total_live_count,
            }
        )
    )
    return following_list


def _chzzk_key(chzzk_id: str) -> dict:
    return {"PK": f"CHZZK#{chzzk_id}", "SK": f"CHZZK#{chzzk_id}"}


def get_chzzk_items(chzzk_ids: list[str]) -> dict[str, dict]:
    """CHZZK 아이템을 BatchGetItem으로 100개씩 읽어 {chzzk_id: item}으로 돌려줍니다."""
    chzzk_ids = list(dict.fromkeys(chzzk_ids))
    items = {}
    unprocessed_ids = []
    failed_ids = []

    for start in range(0, len(chzzk_ids), BATCH_GET_MAX_KEYS):
        chunk_ids = chzzk_ids[start : start + BATCH_GET_MAX_KEYS]
        try:
            unprocessed_ids.extend(_batch_get_chunk(chunk_ids, items))
        except Exception as e:
            chunk_failed_ids = [i for i in chunk_ids if i not in items]
            failed_ids.extend(chunk_failed_ids)
            logger.error(
                json.dumps(
                    {
                        "type": "BATCH_GET_ERROR",
                        "chzzk_ids": chunk_failed_ids,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
            )

    if unprocessed_ids:
        logger.error(
            json.dumps(
                {
                    "type": "BATCH_GET_UNPROCESSED_KEYS",
                    "chzzk_ids": unprocessed_ids,
                }
            )
        )
    missing_ids = [
        chzzk_id
        for chzzk_id in chzzk_ids
        if chzzk_id not in items
        and chzzk_id not in unprocessed_ids
        and chzzk_id not in failed_ids
    ]
    if missing_ids:
        logger.error(
            json.dumps({"type": "GET_DYNAMODB_ERROR", "chzzk_ids": missing_ids})
        )
    return items


def _batch_get_chunk(chunk_ids: list[str], items: dict[str, dict]) -> list[str]:
    """최대 100개 키를 읽어 items에 채우고, 재시도 후에도 남은 키의 chzzk_id를 돌려줍니다."""
    request = {TABLE_NAME: {"Keys": [_chzzk_key(i) for i in chunk_ids]}}
    for attempt in range(BATCH_GET_MAX_ATTEMPTS):
        if attempt:
            time.sleep(BATCH_GET_BACKOFF_SEC * 2 ** (attempt - 1))
        res = table.meta.client.batch_get_item(RequestItems=request)
        for item in res["Responses"].get(TABLE_NAME, []):
            items[item["PK"].removeprefix("CHZZK#")] = item
        request = res.get("UnprocessedKeys") or {}
        if not request:
            return []
    return [key["PK"].removeprefix("CHZZK#") for key in request[TABLE_NAME]["Keys"]]


def update_last_live(chzzk_id: str, chzzk: dict) -> None:
    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={
            "PK": {"S": f"CHZZK#{chzzk_id}"},
            "SK": {"S": f"CHZZK#{chzzk_id}"},
        },
        UpdateExpression="SET lastLiveId = :live_id, lastLiveTitle = :live_title",
        ExpressionAttributeValues={
            ":live_id": {"N": f"{chzzk['liveId']}"},
            ":live_title": {"S": chzzk["liveTitle"] or ""},
        },
    )


def query_notifications(chzzk_id: str) -> list[dict]:
    res = dynamodb.query(
        TableName=TABLE_NAME,
        KeyConditionExpression="PK = :pk_val AND begins_with(SK, :sk_val)",
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": "NOTI#"},
        },
    )
    return res["Items"]


def send_notification(notification_item: dict, data: dict) -> requests.Response:
    return send_notification_message(
        guild_id=notification_item["guild_id"]["S"],
        channel_id=notification_item["channel_id"]["S"],
        data=data,
        notification_item=notification_item,
        crosspost=True,
    )


def update_notification(notification_item: dict, attrs: dict) -> None:
    """attrs({속성 이름: DynamoDB client 형식 값})를 NOTI 아이템에 SET 합니다."""
    names = list(attrs)
    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"PK": notification_item["PK"], "SK": notification_item["SK"]},
        UpdateExpression="SET "
        + ", ".join(f"#a{i} = :a{i}" for i in range(len(names))),
        ExpressionAttributeNames={f"#a{i}": name for i, name in enumerate(names)},
        ExpressionAttributeValues={
            f":a{i}": attrs[name] for i, name in enumerate(names)
        },
    )
