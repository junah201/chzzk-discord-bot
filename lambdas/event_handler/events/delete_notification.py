from datetime import datetime

import boto3
import json

from shared.discord import INTERACTION_CALLBACK_TYPE


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    body = json.loads(event["body"])
    data = body.get("data", {})

    options = data.get("options", [])

    discord_channel_id = options[0].get("value")

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-SK',
        KeyConditionExpression='#sk = :sk_val',
        ExpressionAttributeNames={
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':sk_val': {'S': f"NOTI#{discord_channel_id}"}
        }
    )

    if res.get('Count') == 0:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "embeds": [
                    {
                        "title": f"치지직 알림 삭제 실패",
                        "description": f"<#{discord_channel_id}> 채널에 알림이 존재하지 않습니다.",
                        "color": 0xF01D15,
                        "footer": {
                            "text": "치직"
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                ],
            },
        }

    items = res.get('Items')

    cnt = len(items)

    for item in items:
        dynamodb.delete_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': item.get('PK'),
                'SK': item.get('SK')
            }
        )

    return {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "embeds": [
                {
                    "title": f"알림 삭제 완료",
                    "description": f"<#{discord_channel_id}>에 등록되어 있던 {cnt}개의 채널 알림이 모두 삭제되었습니다.",
                    "color": 0x02E895,
                    "footer": {
                        "text": "치직"
                    },
                    "timestamp": datetime.now().isoformat()
                },
            ],
        },
    }
