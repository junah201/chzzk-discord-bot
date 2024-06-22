"""
특정 시간마다 DynamoDB에 저장된 채널 정보들을 조회하여 채널이 라이브 중일 경우 디스코드 알림을 보냅니다.
"""

import json
from datetime import datetime

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb')


def middleware(event, context):
    index = int(event.get("resources", [])[0][-1])
    request_id = context.aws_request_id
    """
    트리거마다 처리하는 데이터가 다르게 분산화합니다.
    """

    logger.info(
        json.dumps(
            {
                "type": "START",
                "index": index,
                "request_id": request_id
            },
            ensure_ascii=False
        )
    )

    result = {
        "total_channel_count": 0,
        "live_channel_count": 0,
        "total_send_count": 0,
        "fail_send_count": 0,
    }

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-index',
        KeyConditionExpression='#PK = :index_val',
        ExpressionAttributeNames={
            '#PK': 'index'
        },
        ExpressionAttributeValues={
            ':index_val': {'N': f"{index}"}
        }
    )

    logger.info(
        json.dumps(
            {
                "type": "CHANNEL_QUERY_END",
                "total_channel_count": res["Count"],
                "index": index,
                "request_id": request_id
            },
            ensure_ascii=False
        )
    )

    result["total_channel_count"] = res["Count"]

    for item in res["Items"]:
        channel_id = item["PK"]["S"].split("#")[1]
        last_live_id = item["lastLiveId"]["N"]

        try:
            start_time = datetime.now()
            chzzk = get_chzzk(channel_id)
            end_time = datetime.now()
            logger.info(
                json.dumps(
                    {
                        "type": "GET_CHZZK_END",
                        "channel_id": channel_id,
                        "index": index,
                        "time": (end_time - start_time).total_seconds(),
                        "request_id": request_id
                    },
                    ensure_ascii=False
                )
            )
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "GET_CHZZK_ERROR",
                        "channel_id": channel_id,
                        "index": index,
                        "error": str(e),
                        "request_id": request_id
                    }
                )
            )
            continue

        if not chzzk:
            continue

        if str(chzzk['liveId']) == str(last_live_id):
            continue

        if chzzk['status'] != "OPEN":
            continue

        logger.info(
            json.dumps(
                {
                    "type": "LIVE_START",
                    "chzzk_id": channel_id,
                    "index": index,
                    "liveId": chzzk['liveId'],
                    "liveTitle": chzzk['liveTitle'],
                    "request_id": request_id
                }
            )
        )

        result["live_channel_count"] += 1

        dynamodb.update_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': item.get('PK'),
                'SK': item.get('SK')
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
                ':pk_val': {'S': f"CHZZK#{channel_id}"},
                ':sk_val': {'S': 'NOTI#'}
            }
        )

        logger.info(
            json.dumps(
                {
                    "type": "NOTI_QUERY_END",
                    "chzzk_id": channel_id,
                    "index": index,
                    "noti_count": res["Count"],
                    "request_id": request_id
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
                            "url": f"https://chzzk.naver.com/live/{channel_id}",
                            "icon_url": chzzk['channel']['channelImageUrl'] or "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na"
                        },
                        "footer": {
                            "text": "치직"
                        },
                        "url": f"https://chzzk.naver.com/live/{channel_id}",
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
                                "url": f"https://chzzk.naver.com/live/{channel_id}"
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
                logging.error(
                    json.dumps(
                        {
                            "type": "DISCORD_CHANNEL_NOT_FOUND",
                            "chzzk_id": channel_id,
                            "index": index,
                            "discord_channel_id": discord_channel_id,
                            "request_id": request_id
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
                result["fail_send_count"] += 1
                continue

            # 메시지 전송에 실패한 경우
            if res.status_code != 200:

                logging.error(
                    json.dumps(
                        {
                            "type": "DISCORD_MESSAGE_SEND_FAIL",
                            "chzzk_id": channel_id,
                            "index": index,
                            "discord_channel_id": discord_channel_id,
                            "status_code": res.status_code,
                            "response": res.text,
                            "request_id": request_id
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
                result["fail_send_count"] += 1
                continue

            # 성공
            logging.info(
                json.dumps(
                    {
                        "type": "DISCORD_MESSAGE_SEND_SUCCESS",
                        "chzzk_id": channel_id,
                        "index": index,
                        "discord_channel_id": discord_channel_id,
                        "request_id": request_id
                    },
                    ensure_ascii=False
                )
            )
            result["total_send_count"] += 1
            dynamodb.update_item(
                TableName='chzzk-bot-db',
                Key={
                    'PK': noti.get('PK'),
                    'SK': noti.get('SK')
                },
                UpdateExpression='SET last_noti_status = :last_noti_status, last_noti_at = :last_noti_at, noti_fail_count = :noti_fail_count',
                ExpressionAttributeValues={
                    ':last_noti_status': {'S': f"SUCCESS"},
                    ':last_noti_at': {'S': datetime.now().isoformat()},
                    ':noti_fail_count': {'N': "0"}
                }
            )

    return result


def lambda_handler(event, context):
    request_id = context.aws_request_id
    res = middleware(event, context)

    logger.info(
        json.dumps(
            {
                "type": "FINAL_RESULT",
                "result": res,
                "request_id": request_id
            },
            ensure_ascii=False
        )
    )
