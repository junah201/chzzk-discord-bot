"""
DynamoDB에 알림 데이터를 저장합니다.
"""

import json
import logging

import boto3
import requests
from user_agent import generate_user_agent

from shared import get_channel, get_chzzk, middleware

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table("chzzk-bot-db")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    # get authorization header
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id", None)
    channel_id = body.get("channel_id", None)
    custom_message = body.get("custom_message", None)
    disable_embed = body.get("disable_embed", False)
    disable_button = body.get("disable_button", False)
    disable_notification = body.get("disable_notification", False)

    for i in [token, chzzk_id, channel_id, custom_message]:
        if i is None:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "message": "token, chzzk_id, channel_id, custom_message are required"
                    }
                ),
            }

    # 디스코드 채널 정보 확인
    channel_data = get_channel(channel_id)
    if not channel_data:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "해당 디스코드 채널을 찾을 수 없습니다."}),
        }

    # 치지직 채널이 있는지 확인
    chzzk = get_chzzk(chzzk_id)
    if not chzzk:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "해당 치지직 채널을 찾을 수 없습니다."}),
        }

    index = int(chzzk_id, 16) % 7

    # 치지직 채널 정보가 등록되어 있는지 확인
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"CHZZK#{chzzk_id}"},
        },
    )
    if not res.get("Items", []):
        res = dynamodb.put_item(
            TableName="chzzk-bot-db",
            Item={
                "PK": {"S": f"CHZZK#{chzzk_id}"},
                "SK": {"S": f"CHZZK#{chzzk_id}"},
                "lastLiveId": {"N": f"{chzzk['liveId']}"},
                "lastLiveTitle": {"S": chzzk["liveTitle"]},
                "channelId": {"S": chzzk["channel"]["channelId"]},
                "channelName": {"S": chzzk["channel"]["channelName"]},
                "channelImageUrl": {"S": chzzk["channel"]["channelImageUrl"] or ""},
                "type": {"S": "CHZZK"},
                "index": {"N": f"{index}"},
            },
        )

        # 업로드 실패
        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"message": "치지직 채널 정보 등록에 실패했습니다."}
                ),
            }

    # 네이버 계정 가져오기
    naver = table.get_item(Key={"PK": f"NAVER#{index}", "SK": f"NAVER#{index}"})

    # 팔로우 요청
    if naver.get("Item"):
        naver = naver["Item"]
        NID_AUT = naver.get("NID_AUT")
        NID_SES = naver.get("NID_SES")

        res = requests.post(
            f"https://api.chzzk.naver.com/service/v1/channels/{chzzk_id}/follow",
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}",
            },
            timeout=2,
        )

        if res.status_code != 200:
            logger.error(
                json.dumps(
                    {
                        "type": "CHZZK_FOLLOW_ERROR",
                        "status_code": res.status_code,
                        "text": res.text,
                    },
                    ensure_ascii=False,
                )
            )
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"message": "치지직 채널 팔로우에 실패했습니다. 다시 시도해주세요."}
                ),
            }

        logger.info(
            json.dumps(
                {"type": "CHZZK_FOLLOW_SUCCESS", "channel_id": chzzk_id},
                ensure_ascii=False,
            )
        )

    # 이미 등록된 알림인지 확인
    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="#pk = :pk_val AND #sk = :sk_val",
        ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"NOTI#{channel_id}"},
        },
    )
    if res.get("Items", []):
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "message": f"이미 {channel_data['name']}에 등록된 채널({chzzk['channel']['channelName']})입니다."
                }
            ),
        }

    dynamodb.put_item(
        TableName="chzzk-bot-db",
        Item={
            "PK": {"S": f"CHZZK#{chzzk_id}"},
            "SK": {"S": f"NOTI#{channel_id}"},
            "channel_id": {"S": f"{channel_id}"},
            "channel_name": {"S": channel_data.get("name", "")},
            "guild_id": {"S": channel_data.get("guild_id", "")},
            "custom_message": {"S": custom_message},
            "type": {"S": "NOTI"},
            "disable_embed": {"BOOL": disable_embed},
            "disable_button": {"BOOL": disable_button},
            "disable_notification": {"BOOL": disable_notification},
            "index": {"N": "-1"},
        },
    )

    return {
        "statusCode": 204,
    }
