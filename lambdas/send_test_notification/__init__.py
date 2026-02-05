import json
import logging
from datetime import datetime

import boto3

from shared import get_chzzk, middleware, send_message
from shared.discord import BUTTON_STYLE, COMPONENT_TYPE
from shared.exceptions import BadRequestError

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id", None)
    discord_channel_id = body.get("channel_id", None)

    if not all([chzzk_id, discord_channel_id]):
        raise BadRequestError()

    # 치지직 채널이 있는지 확인
    chzzk = get_chzzk(chzzk_id)
    if not chzzk:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "해당 치지직 채널을 찾을 수 없습니다."}),
        }

    res = dynamodb.query(
        TableName="chzzk-bot-db",
        KeyConditionExpression="PK = :pk_val AND begins_with(SK, :sk_val)",
        ExpressionAttributeValues={
            ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
            ":sk_val": {"S": f"NOTI#{discord_channel_id}"},
        },
    )

    if res["Count"] < 1:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "해당 알림이 존재하지 않습니다."}),
        }

    item = res["Items"][0]

    data = {
        "content": "관리자의 요청에 따라 전송된 테스트 알림입니다."
        + "\n\n"
        + item.get("custom_message", {}).get("S", "")
    }
    if not item.get("disable_embed", {"BOOL": False})["BOOL"]:
        data["embeds"] = [
            {
                "title": f"{chzzk['liveTitle']}",
                "description": f"{chzzk['channel']['channelName']} 님이 방송을 시작했습니다.",
                "color": 0x02E895,
                "fields": [{"name": "카테고리", "value": chzzk["liveCategoryValue"]}],
                "image": {
                    "url": (
                        chzzk["liveImageUrl"]
                        or chzzk["channel"]["channelImageUrl"]
                        or ""
                    ).replace("_{type}", "_1080"),
                },
                "author": {
                    "name": f"{chzzk['channel']['channelName']}",
                    "url": f"https://chzzk.naver.com/live/{chzzk_id}",
                    "icon_url": chzzk["channel"]["channelImageUrl"]
                    or "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na",
                },
                "footer": {"text": "chzzk.junah.dev"},
                "url": f"https://chzzk.naver.com/live/{chzzk_id}",
                "timestamp": datetime.now().isoformat(),
            },
        ]
    if not item.get("disable_button", {"BOOL": False})["BOOL"]:
        data["components"] = [
            {
                "type": COMPONENT_TYPE.ACTION_ROW,
                "components": [
                    {
                        "type": COMPONENT_TYPE.BUTTON,
                        "label": "바로가기",
                        "style": BUTTON_STYLE.LINK,
                        "url": f"https://chzzk.naver.com/live/{chzzk_id}",
                    }
                ],
            },
        ]

    res = send_message(channel_id=discord_channel_id, data=data)

    # 채널이 존재하지 않는 경우
    if res.status_code == 404:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_CHANNEL_NOT_FOUND",
                    "status_code": res.status_code,
                    "response": res.text,
                    "channel_id": discord_channel_id,
                    "chzzk_id": chzzk_id,
                    "data": data,
                },
                ensure_ascii=False,
            )
        )
        dynamodb.delete_item(
            TableName="chzzk-bot-db", Key={"PK": item.get("PK"), "SK": item.get("SK")}
        )
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "해당 디스코드 채널이 존재하지 않습니다."}),
        }

    # 메시지 전송에 실패한 경우
    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "SEND_MESSAGE_FAIL",
                    "status_code": res.status_code,
                    "response": res.text,
                    "channel_id": discord_channel_id,
                    "chzzk_id": chzzk_id,
                    "data": data,
                },
                ensure_ascii=False,
            )
        )
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": f"테스트 알림 전송에 실패했습니다. 치직 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인해주세요. ({res.json()})"
                }
            ),
        }

    # 성공
    logger.info(
        json.dumps(
            {
                "type": "SEND_MESSAGE_SUCCESS",
                "channel_id": discord_channel_id,
                "chzzk_id": chzzk_id,
                "data": data,
            },
            ensure_ascii=False,
        )
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "테스트 알림을 성공적으로 전송했습니다."}),
    }
