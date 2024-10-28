import json
import logging
import traceback
from datetime import datetime
from typing import Tuple

import boto3
import requests
from user_agent import generate_user_agent

from shared import *

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')
table = boto3.resource('dynamodb').Table('chzzk-bot-db')


def get_follows(NID_AUT: str, NID_SES: str) -> list[Following]:
    page = 0
    total_page = 1

    follows = list()

    while page < total_page:
        res = requests.get(
            "https://api.chzzk.naver.com/service/v1/channels/followings",
            params={
                "page": page,
                "size": 505,
                "sortType": "FOLLOW",
                "subscription": False,
                "followerCount": False
            },
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}"
            }
        )
        data = res.json()
        total_page = data.get("content", {}).get("totalPage", 0)
        page += 1

        follows.extend(data.get("content", {}).get("followingList", []))

        if res.status_code != 200:
            logging.error(
                json.dumps(
                    {
                        "type": "GET_FOLLOWING_ERROR",
                        "status_code": res.status_code,
                        "text": res.text,
                        "page": page
                    },
                    ensure_ascii=False
                )
            )
            continue

        logger.info(
            json.dumps(
                {
                    "type": "GET_FOLLOWING_SUCCESS",
                    "page": page,
                    "total_page": total_page,
                    "count": len(data.get("content", {}).get("followingList", []))
                }
            )
        )

    return follows


def send_notification(chzzk_id: str):
    live_start_cnt = 0
    noti_send_cnt = 0
    noti_fail_cnt = 0

    res = table.get_item(
        Key={
            "PK": f"CHZZK#{chzzk_id}",
            "SK": f"CHZZK#{chzzk_id}"
        }
    )
    item = res.get("Item", None)

    if not item:
        logger.error(
            json.dumps(
                {
                    "type": "GET_DYNAMODB_ERROR",
                    "chzzk_id": chzzk_id,
                    "ResponseMetadata": res.get("ResponseMetadata", None)
                }
            )
        )
        return live_start_cnt, noti_send_cnt, noti_fail_cnt

    last_live_id = item["lastLiveId"]

    try:
        start_time = datetime.now()
        chzzk = get_chzzk(chzzk_id, logger=logger)
        end_time = datetime.now()
        logger.info(
            json.dumps(
                {
                    "type": "GET_CHZZK_END",
                    "channel_id": chzzk_id,
                    "time": (end_time - start_time).total_seconds(),
                    "chzzk": {
                        "liveId": (chzzk or {}).get("liveId", None),
                        "liveTitle": (chzzk or {}).get("liveTitle", None),
                        "status": (chzzk or {}).get("status", None)
                    }
                },
                ensure_ascii=False
            )
        )
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "GET_CHZZK_ERROR",
                    "channel_id": chzzk_id,
                    "error": str(e)
                }
            )
        )
        return live_start_cnt, noti_send_cnt, noti_fail_cnt

    if not chzzk:
        return live_start_cnt, noti_send_cnt, noti_fail_cnt

    if str(chzzk['liveId']) == str(last_live_id):
        logger.debug(
            json.dumps(
                {
                    "type": "LIVE_NOT_CHANGED",
                    "chzzk_id": chzzk_id,
                    "liveId": chzzk['liveId'],
                }
            )
        )
        return live_start_cnt, noti_send_cnt, noti_fail_cnt

    live_start_cnt += 1
    logger.info(
        json.dumps(
            {
                "type": "LIVE_START",
                "chzzk_id": chzzk_id,
                "liveId": chzzk['liveId'],
                "liveTitle": chzzk['liveTitle'],
            }
        )
    )
    dynamodb.update_item(
        TableName='chzzk-bot-db',
        Key={
            'PK': {"S": f"CHZZK#{chzzk_id}"},
            'SK': {"S": f"CHZZK#{chzzk_id}"},
        },
        UpdateExpression='SET lastLiveId = :live_id, lastLiveTitle = :live_title',
        ExpressionAttributeValues={
            ':live_id': {'N': f"{chzzk['liveId']}"},
            ':live_title': {'S': chzzk['liveTitle']}
        }
    )

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='PK = :pk_val AND begins_with(SK, :sk_val)',
        ExpressionAttributeValues={
            ':pk_val': {'S': f"CHZZK#{chzzk_id}"},
            ':sk_val': {'S': 'NOTI#'}
        }
    )

    logger.info(
        json.dumps(
            {
                "type": "NOTI_QUERY_END",
                "chzzk_id": chzzk_id,
                "noti_count": res["Count"],
            },
            ensure_ascii=False
        ),
    )

    for noti in res["Items"]:
        discord_channel_id = noti["channel_id"]["S"]

        data = {
            "content": noti.get("custom_message", {}).get("S", ""),
        }
        if not noti.get("disable_embed", {"BOOL": False})["BOOL"]:
            data["embeds"] = [
                {
                    "title": f"{chzzk['liveTitle']}",
                    "description": f"{chzzk['channel']['channelName']} 님이 방송을 시작했습니다.",
                    "color": 0x02E895,
                    "fields": [
                        {
                            "name": '카테고리',
                            "value": chzzk['liveCategoryValue']
                        }
                    ],
                    "image": {
                        "url": (chzzk['liveImageUrl'] or chzzk['channel']['channelImageUrl'] or "").replace("_{type}", "_1080"),
                    },
                    "author": {
                        "name": f"{chzzk['channel']['channelName']}",
                        "url": f"https://chzzk.naver.com/live/{chzzk_id}",
                        "icon_url": chzzk['channel']['channelImageUrl'] or "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na"
                    },
                    "footer": {
                        "text": "chzzk.junah.dev"
                    },
                    "url": f"https://chzzk.naver.com/live/{chzzk_id}",
                    "timestamp": datetime.now().isoformat()
                },
            ]
        if not noti.get("disable_button", {"BOOL": False})["BOOL"]:
            data["components"] = [
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.BUTTON,
                            "label": "바로가기",
                            "style": BUTTON_STYLE.LINK,
                            "url": f"https://chzzk.naver.com/live/{chzzk_id}"
                        }
                    ]
                },
            ]

        res = send_message(
            channel_id=discord_channel_id,
            data=data
        )

        # 채널이 존재하지 않는 경우
        if res.status_code == 404:
            noti_fail_cnt += 1
            logging.error(
                json.dumps(
                    {
                        "type": "DISCORD_CHANNEL_NOT_FOUND",
                        "chzzk_id": chzzk_id,
                        "discord_channel_id": discord_channel_id,
                    },
                    ensure_ascii=False
                )
            )
            dynamodb.delete_item(
                TableName='chzzk-bot-db',
                Key={
                    'PK': noti.get('PK'),
                    'SK': noti.get('SK')
                }
            )
            continue

        # 메시지 전송에 실패한 경우
        if res.status_code != 200:
            noti_fail_cnt += 1
            logging.error(
                json.dumps(
                    {
                        "type": "DISCORD_MESSAGE_SEND_FAIL",
                        "chzzk_id": chzzk_id,
                        "discord_channel_id": discord_channel_id,
                        "status_code": res.status_code,
                        "response": res.text,
                    },
                    ensure_ascii=False
                ),
            )
            dynamodb.update_item(
                TableName='chzzk-bot-db',
                Key={
                    'PK': noti.get('PK'),
                    'SK': noti.get('SK')
                },
                UpdateExpression='SET last_noti_status = :last_noti_status, last_noti_at = :last_noti_at, noti_fail_count = :noti_fail_count',
                ExpressionAttributeValues={
                    ':last_noti_status': {'S': f"FAIL_{res.status_code}"},
                    ':last_noti_at': {'S': datetime.now().isoformat()},
                    ':noti_fail_count': {'N': str(int(noti.get("noti_fail_count", {"N": "0"})["N"]) + 1)}
                }
            )
            continue

        # 성공
        noti_send_cnt += 1
        logging.info(
            json.dumps(
                {
                    "type": "DISCORD_MESSAGE_SEND_SUCCESS",
                    "chzzk_id": chzzk_id,
                    "discord_channel_id": discord_channel_id,
                },
                ensure_ascii=False
            )
        )
        dynamodb.update_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': noti.get('PK'),
                'SK': noti.get('SK')
            },
            UpdateExpression='SET last_noti_status = :last_noti_status, last_noti_at = :last_noti_at, noti_fail_count = :noti_fail_count',
            ExpressionAttributeValues={
                ':last_noti_status': {'S': "SUCCESS"},
                ':last_noti_at': {'S': datetime.now().isoformat()},
                ':noti_fail_count': {'N': "0"}
            }
        )

    return live_start_cnt, noti_send_cnt, noti_fail_cnt


@middleware(logger)
def handler(event, context):
    index = int(event.get("resources", [])[0][-1])
    request_id = context.aws_request_id

    res = table.get_item(
        Key={
            "PK": f"NAVER#{index}",
            "SK": f"NAVER#{index}"
        }
    )
    naver = res.get("Item")

    NID_AUT = naver.get("NID_AUT")
    NID_SES = naver.get("NID_SES")

    follows = get_follows(NID_AUT, NID_SES)
    live_channels: list[str] = [
        f["channel"]["channelId"]
        for f in follows if f["streamer"]["openLive"] == True
    ]
    logger.info(
        json.dumps(
            {
                "type": "GET_FOLLOWINGS_SUCCESS",
                "follows_count": len(follows),
                "live_count": len(live_channels)
            }
        )
    )

    total_live_start_cnt = 0
    total_noti_send_cnt = 0
    total_noti_fail_cnt = 0

    for chzzk_id in live_channels:
        try:
            live_start_cnt, noti_send_cnt, noti_fail_cnt = send_notification(
                chzzk_id)
            total_live_start_cnt += live_start_cnt
            total_noti_send_cnt += noti_send_cnt
            total_noti_fail_cnt += noti_fail_cnt
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "SEND_NOTIFICATION_ERROR",
                        "chzzk_id": chzzk_id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
            )

    logger.info(
        json.dumps(
            {
                "type": "LIVE_CHECK_RESULT",
                "index": index,
                "request_id": request_id,
                "total_follows_count": len(follows),
                "total_live_channels_count": len(live_channels),
                "total_live_start_cnt": total_live_start_cnt,
                "total_noti_send_cnt": total_noti_send_cnt,
                "total_noti_fail_cnt": total_noti_fail_cnt
            }
        )
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "index": index,
                "request_id": request_id,
                "total_follows_count": len(follows),
                "total_live_channels_count": len(live_channels),
                "total_live_start_cnt": total_live_start_cnt,
                "total_noti_send_cnt": total_noti_send_cnt,
                "total_noti_fail_cnt": total_noti_fail_cnt
            }
        )
    }
