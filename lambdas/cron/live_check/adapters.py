import json
import logging
import os
from datetime import UTC, datetime

import boto3
import requests
from shared import Following, get_chzzk, send_message
from shared.notification_dispatcher import send_notification_message
from user_agent import generate_user_agent

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID"
)

CHZZK_FOLLOWINGS_TIMEOUT_SEC = 10
TABLE_NAME = "chzzk-bot-db"

logger = logging.getLogger()

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def get_naver_session(index: int) -> tuple[str, str]:
    res = table.get_item(Key={"PK": "NAVER#ACCOUNTS", "SK": f"NAVER#{index}"})
    naver = res.get("Item")
    return naver.get("NID_AUT"), naver.get("NID_SES")


def get_follows(NID_AUT: str, NID_SES: str, index: int) -> list[Following]:
    page = 0
    total_page = 1

    follows = []

    while page < total_page:
        res = requests.get(
            "https://api.chzzk.naver.com/service/v1/channels/followings",
            params={
                "page": page,
                "size": 505,
                "sortType": "FOLLOW",
                "subscription": False,
                "followerCount": False,
            },
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}",
            },
            timeout=CHZZK_FOLLOWINGS_TIMEOUT_SEC,
        )
        data = res.json()
        total_page = data.get("content", {}).get("totalPage", 0)
        page += 1

        follows.extend(data.get("content", {}).get("followingList", []))

        if res.status_code != 200:
            logger.error(
                json.dumps(
                    {
                        "type": "GET_FOLLOWING_ERROR",
                        "status_code": res.status_code,
                        "text": res.text,
                        "page": page,
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
                            "description": f"Failed to get following list. Status code: {res.status_code}",
                            "color": 0xFF0000,
                            "fields": [
                                {"name": "page", "value": str(page)},
                                {"name": "text", "value": res.text},
                                {"name": "index", "value": str(index)},
                            ],
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    ]
                },
                token=ADMIN_DISCORD_TOKEN,
            )
            continue

        logger.info(
            json.dumps(
                {
                    "type": "GET_FOLLOWING_SUCCESS",
                    "page": page,
                    "total_page": total_page,
                    "count": len(data.get("content", {}).get("followingList", [])),
                    "index": index,
                }
            )
        )

    return follows


def get_chzzk_item(chzzk_id: str) -> tuple[dict | None, dict | None]:
    """CHZZK 아이템과, 없을 때 로그에 남길 ResponseMetadata를 반환합니다."""
    res = table.get_item(Key={"PK": f"CHZZK#{chzzk_id}", "SK": f"CHZZK#{chzzk_id}"})
    return res.get("Item", None), res.get("ResponseMetadata", None)


def fetch_live(chzzk_id: str) -> dict | None:
    return get_chzzk(chzzk_id, logger=logger)


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
            ":live_title": {"S": chzzk["liveTitle"]},
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
