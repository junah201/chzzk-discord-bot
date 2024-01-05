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
            ':guild_id': {'S': f'{guild_id}'}
        }
    )

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(res.get('Items'))
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
