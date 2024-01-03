import boto3

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    body = event.get("body", {})
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
            ':sk_val': {'S': f'NOTI#{discord_channel_id}'}
        }
    )

    if res.get('Count') == 0:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"해당 채널에 알림이 존재하지 않습니다.",
            },
        }

    for item in res.get('Items'):
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
            "content": f"해당 채널에 등록되어 있던 치지직 알림이 모두 삭제되었습니다.",
        }
    }
