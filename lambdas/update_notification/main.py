"""
저장된 알림의 커스텀 메시지를 수정합니다.
"""

import json

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

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='#pk = :pk_val AND #sk = :sk_val',
        ExpressionAttributeNames={
            '#pk': 'PK',
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':pk_val': {'S': f"CHZZK#{chzzk_id}"},
            ':sk_val': {'S': f"NOTI#{channel_id}"}
        }
    )

    if res["Count"] < 1:
        return {
            "statusCode": 404,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "해당 알림을 찾을 수 없습니다."}),
        }

    item = res["Items"][0]
    item["custom_message"] = {
        "S": custom_message
    }

    res = dynamodb.put_item(
        TableName='chzzk-bot-db',
        Item=item
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
