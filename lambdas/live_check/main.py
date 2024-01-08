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

dynamodb = boto3.client('dynamodb')


def middleware(event, context):
    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-type',
        KeyConditionExpression='#PK = :type_val',
        ExpressionAttributeNames={
            '#PK': 'type'
        },
        ExpressionAttributeValues={
            ':type_val': {'S': f'CHZZK'}
        }
    )

    for item in res["Items"]:
        print(item)
        channel_id = item["PK"]["S"].split("#")[1]
        last_live_id = item["lastLiveId"]["N"]

        chzzk = get_chzzk(channel_id)

        if not chzzk:
            continue

        if str(chzzk.liveId) == str(last_live_id):
            continue

        if chzzk.status != "OPEN":
            continue

        res = dynamodb.query(
            TableName='chzzk-bot-db',
            KeyConditionExpression='PK = :pk_val AND begins_with(SK, :sk_val)',
            ExpressionAttributeValues={
                ':pk_val': {'S': f'CHZZK#{channel_id}'},
                ':sk_val': {'S': 'NOTI#'}
            }
        )

        for noti in res["Items"]:
            discord_channel_id = noti["channel_id"]["S"]

            res = send_message(
                channel_id=discord_channel_id,
                data={
                    "content": "",
                    "embeds": [
                        {
                            "title": f"{chzzk.liveTitle}",
                            "description": f"{chzzk.channel.channelName} 님이 방송을 시작했습니다.",
                            "color": 0x02E895,
                            "fields": [
                                {
                                    "name": '카테고리',
                                    "value": chzzk.liveCategoryValue
                                }
                            ],
                            "image": {
                                "url": chzzk.liveImageUrl.replace("_{type}", "_1080"),
                            },
                            "author": {
                                "name": f"{chzzk.channel.channelName}",
                                "url": f"https://chzzk.naver.com/live/{channel_id}",
                                "icon_url": f"{chzzk.channel.channelImageUrl}"
                            },
                            "footer": {
                                "text": "치직"
                            },
                            "url": f"https://chzzk.naver.com/live/{channel_id}",
                            "timestamp": datetime.now().isoformat()
                        },
                    ],
                    "components": [
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
                    ],
                }
            )

            # 채널이 존재하지 않는 경우
            if res.status_code == 404:
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
                continue

        dynamodb.update_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': item.get('PK'),
                'SK': item.get('SK')
            },
            UpdateExpression='SET lastLiveId = :live_id, lastLiveTitle = :live_title',
            ExpressionAttributeValues={
                ':live_id': {'N': f'{chzzk.liveId}'},
                ':live_title': {'S': chzzk.liveTitle}
            }
        )


def lambda_handler(event, context):
    res = middleware(event, context)

    print("res", json.dumps(res))

    return res
