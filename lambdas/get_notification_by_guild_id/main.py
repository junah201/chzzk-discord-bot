"""
특정 ID의 디스코드 서버의 알림 목록을 가져옵니다.
데이터가 없을 경우 빈 리스트를 반환합니다.
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
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-GuildID',
        KeyConditionExpression='guild_id = :guild_id',
        ExpressionAttributeValues={
            ':guild_id': {'S': f"{guild_id}"}
        }
    )

    result = [
        {
            "PK": item.get('PK', {}).get('S'),
            "SK": item.get('SK', {}).get('S'),
            "guild_id": item.get('guild_id', {}).get('S'),
            "channel_id": item.get('channel_id', {}).get('S'),
            "channel_name": item.get('channel_name', {}).get('S'),
            "custom_message": item.get('custom_message', {}).get('S'),
        }

        for item in res.get('Items')
    ]

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(result)
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
