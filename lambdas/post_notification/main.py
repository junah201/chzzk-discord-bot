"""
DynamoDB에 알림 데이터를 저장합니다.
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
    # get authorization header
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id", None)
    channel_id = body.get("channel_id", None)
    custom_message = body.get("custom_message", None)

    for i in [token, chzzk_id, channel_id, custom_message]:
        if i is None:
            return {
                "statusCode": 400,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({"message": "token, chzzk_id, channel_id, custom_message are required"}),
            }

    # 디스코드 채널 정보 확인
    channel_data = get_channel(channel_id)
    if not channel_data:
        return {
            "statusCode": 400,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "해당 디스코드 채널을 찾을 수 없습니다."}),
        }

    # 치지직 채널이 있는지 확인
    chzzk = get_chzzk(chzzk_id)
    if not chzzk:
        return {
            "statusCode": 400,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "해당 치지직 채널을 찾을 수 없습니다."}),
        }

    # 치지직 채널 정보가 등록되어 있는지 확인
    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='#pk = :pk_val AND #sk = :sk_val',
        ExpressionAttributeNames={
            '#pk': 'PK',
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':pk_val': {'S': f'CHZZK#{chzzk_id}'},
            ':sk_val': {'S': f'CHZZK#{chzzk_id}'}
        }
    )
    if not res.get('Items', []):
        res = dynamodb.put_item(
            TableName='chzzk-bot-db',
            Item={
                'PK': {'S': f'CHZZK#{chzzk_id}'},
                'SK': {'S': f'CHZZK#{chzzk_id}'},
                'lastLiveId': {'N': f"{chzzk.liveId}"},
                'lastLiveTitle': {'S': chzzk.liveTitle},
                'channelId': {'S': chzzk.channel.channelId},
                'channelName': {'S': chzzk.channel.channelName},
                'channelImageUrl': {'S': chzzk.channel.channelImageUrl or ""},
                "type": {"S": "CHZZK"},
                "index": {"N": f"{int(chzzk_id, 16) % 6}"}
            }
        )

        # 업로드 실패
        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {
                "statusCode": 500,
                "headers": {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                "body": json.dumps({"message": "치지직 채널 정보 등록에 실패했습니다."}),
            }

    # 이미 등록된 알림인지 확인
    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='#pk = :pk_val AND #sk = :sk_val',
        ExpressionAttributeNames={
            '#pk': 'PK',
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':pk_val': {'S': f'CHZZK#{chzzk_id}'},
            ':sk_val': {'S': f'NOTI#{channel_id}'}
        }
    )
    if res.get('Items', []):
        return {
            "statusCode": 400,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": f"이미 {channel_data['name']}에 등록된 채널({chzzk.channel.channelName})입니다."}),
        }

    dynamodb.put_item(
        TableName='chzzk-bot-db',
        Item={
            'PK': {'S': f'CHZZK#{chzzk_id}'},
            'SK': {'S': f'NOTI#{channel_id}'},
            'channel_id': {'S': f'{channel_id}'},
            'channel_name': {'S': channel_data.get('name', '')},
            'guild_id': {'S': channel_data.get('guild_id', '')},
            "custom_message": {'S': custom_message},
            "index": {"N": "-1"}
        }
    )

    return {
        "statusCode": 204,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
