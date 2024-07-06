import json
import boto3
import logging

from shared import middleware

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    # get authorization header
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    body = json.loads(event.get("body", "{}"))

    chzzk_id = body.get("chzzk_id", None)
    channel_id = body.get("channel_id", None)
    custom_message = body.get("custom_message", None)
    disable_embed = body.get("disable_embed", False)
    disable_button = body.get("disable_button", False)

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
    item["custom_message"] = {"S": custom_message}
    item["disable_embed"] = {"BOOL": disable_embed}
    item["disable_button"] = {"BOOL": disable_button}

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
