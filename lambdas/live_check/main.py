"""
특정 시간마다 DynamoDB에 저장된 채널 정보들을 조회하여 채널이 라이브 중일 경우 디스코드 알림을 보냅니다.
"""

import json

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import boto3

dynamodb = boto3.client('dynamodb')


def middleware(event, context):
    res = dynamodb.scan(
        TableName='chzzk-bot-db',
        FilterExpression='SK >= :sk_start AND SK < :sk_end',
        ExpressionAttributeValues={
            ':sk_start': {'S': f"CHZZK#"},
            ':sk_end': {'S': f'NOTI#'},
        }
    )

    for item in res["Items"]:
        print(item)
        channel_id = item["channelId"]["S"]
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

            send_message(
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
                                "url": f"https://chzzk.naver.com/live/${channel_id}",
                                "icon_url": f"{chzzk.channel.channelImageUrl}"
                            },
                            "footer": {
                                "text": "Chizz BOT"
                            },
                            "url": f"https://chzzk.naver.com/live/${channel_id}",
                            "timestamp": f"{chzzk.openDate}"
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
                                    "url": f"https://chzzk.naver.com/live/${channel_id}"
                                }
                            ]
                        },
                    ],
                }
            )

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
