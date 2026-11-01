import json
import logging
import os
import time
from datetime import UTC, datetime

import boto3
import requests
from shared import dynamo_to_python
from shared.discord.utils import send_message
from shared.utils import mask_secret
from user_agent import generate_user_agent

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_NAVER_SESSION_RENEW_EXPIRED_CHANNEL_ID = os.environ.get(
    "DISCORD_NAVER_SESSION_RENEW_EXPIRED_CHANNEL_ID"
)
# 계정 7개 × (요청 5초 + 대기 1.5초)가 Lambda timeout(60초) 안에 끝나야 한다.
NAVER_REQUEST_TIMEOUT_SEC = 5

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(_event, context):
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :val",
        ExpressionAttributeNames={"#pk": "PK"},
        ExpressionAttributeValues={":val": {"S": "NAVER#ACCOUNTS"}},
    )

    items = [dynamo_to_python(item) for item in res.get("Items", [])]
    items.sort(key=lambda x: x.get("SK"))

    result = []

    for item in items:
        NID_AUT = item.get("NID_AUT")
        NID_SES = item.get("NID_SES")

        try:
            res = requests.get(
                "https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus",
                headers={
                    "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                    "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}",
                },
                timeout=NAVER_REQUEST_TIMEOUT_SEC,
            )
        except requests.RequestException as e:
            # 한 계정의 네트워크 오류가 나머지 계정 갱신을 막지 않도록 실패로 처리하고 넘어간다.
            logger.error(
                json.dumps(
                    {
                        "type": "NAVER_SESSION_RENEW_REQUEST_ERROR",
                        "SK": item.get("SK"),
                        "error": str(e),
                    }
                )
            )
            NEW_NID_SES = "error"
        else:
            try:
                NEW_NID_SES = (
                    res.headers["set-cookie"].split("NID_SES=")[1].split(";")[0]
                )
            except Exception as e:
                logger.error(
                    json.dumps(
                        {
                            "type": "NAVER_SESSION_RENEW_ERROR",
                            "PK": item.get("PK"),
                            "error": str(e),
                            "text": res.text,
                        }
                    )
                )
                NEW_NID_SES = "error"

        if NEW_NID_SES not in ["expired", "error"]:
            dynamodb.update_item(
                TableName="chzzk-bot-db",
                Key={"PK": {"S": item.get("PK")}, "SK": {"S": item.get("SK")}},
                UpdateExpression="SET NID_SES = :val",
                ExpressionAttributeValues={":val": {"S": NEW_NID_SES}},
            )
        else:
            logger.error(
                json.dumps(
                    {
                        "type": "NAVER_SESSION_RENEW_EXPIRED",
                        "SK": item.get("SK"),
                        "NID_AUT": mask_secret(NID_AUT),
                        "NID_SES": mask_secret(NID_SES),
                    }
                )
            )

            res = send_message(
                channel_id=DISCORD_NAVER_SESSION_RENEW_EXPIRED_CHANNEL_ID,
                data={
                    "embeds": [
                        {
                            "title": "NAVER_SESSION_RENEW_EXPIRED",
                            "description": "Naver session renewal failed. The session has expired or an error occurred.",
                            "color": 0xFF0000,
                            "fields": [
                                {
                                    "name": "SK",
                                    "value": f"`{item.get('SK')}`",
                                    "inline": False,
                                },
                                {
                                    "name": "NID_AUT",
                                    "value": f"`{mask_secret(NID_AUT)}`",
                                    "inline": False,
                                },
                                {
                                    "name": "NID_SES",
                                    "value": f"`{mask_secret(NID_SES)}`",
                                    "inline": False,
                                },
                            ],
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    ]
                },
                token=ADMIN_DISCORD_TOKEN,
            )
            logger.info(
                json.dumps(
                    {
                        "type": "DISCORD_MESSAGE_SENT",
                        "channel_id": DISCORD_NAVER_SESSION_RENEW_EXPIRED_CHANNEL_ID,
                        "status_code": res.status_code,
                        "text": res.text,
                    }
                )
            )

        result.append(
            {
                "SK": item.get("SK"),
                "NID_AUT": mask_secret(NID_AUT),
                "ORIGINAL_NID_SES": mask_secret(NID_SES),
                "NEW_NID_SES": mask_secret(NEW_NID_SES)
                if NEW_NID_SES not in ["expired", "error"]
                else NEW_NID_SES,
            }
        )
        time.sleep(1.5)

    logger.info(json.dumps({"type": "NAVER_SESSION_RENEW", "result": result}))

    return result
