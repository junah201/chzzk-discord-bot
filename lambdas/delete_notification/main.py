"""
알림을 삭제합니다.
만약 해당 알림이 없으면 404를 반환합니다.
"""

import json

import boto3

dynamodb = boto3.client('dynamodb')


def middleware(event, context):
    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id", None)
    channel_id = body.get("channel_id", None)

    if channel_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "channel_id is required"}),
        }

    if chzzk_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "chzzk_id is required"}),
        }

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='PK = :pk_val AND SK = :sk_val',
        ExpressionAttributeValues={
            ':pk_val': {'S': f'CHZZK#{chzzk_id}'},
            ':sk_val': {'S': f'NOTI#{channel_id}'}
        }
    )

    if res.get('Count') == 0:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "해당 알림을 찾을 수 없습니다."}),
        }

    dynamodb.delete_item(
        TableName='chzzk-bot-db',
        Key={
            'PK': f'CHZZK#{chzzk_id}',
            'SK': f'NOTI#{channel_id}'
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
