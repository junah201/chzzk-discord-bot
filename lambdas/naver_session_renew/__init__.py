import json
import boto3
import logging
import requests
from user_agent import generate_user_agent
from shared import dynamo_to_python
import time

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-type',
        KeyConditionExpression='#type = :val',
        ExpressionAttributeNames={
            '#type': 'type'
        },
        ExpressionAttributeValues={
            ':val': {'S': "NAVER"}
        }
    )

    items = [
        dynamo_to_python(item)
        for item in res.get('Items', [])
    ]

    result = list()

    for item in items:
        NID_AUT = item.get("NID_AUT")
        NID_SES = item.get("NID_SES")

        res = requests.get(
            f"https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus",
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={NID_AUT}; NID_SES={NID_SES}"
            },
        )
        NEW_NID_SES = res.headers["set-cookie"].split("NID_SES=")[
            1].split(";")[0]

        dynamodb.update_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': {'S': item.get("PK")},
                'SK': {'S': item.get("SK")}
            },
            UpdateExpression='SET NID_SES = :val',
            ExpressionAttributeValues={
                ':val': {'S': NEW_NID_SES}
            }
        )
        result.append({
            "PK": item.get("PK"),
            "ORIGINAL_NID_SES": f"{NID_SES[:7]}...{NID_SES[-7:]}",
            "NEW_NID_SES": f"{NEW_NID_SES[:7]}...{NEW_NID_SES[-7:]}"
        })
        time.sleep(0.5)

    logger.info(
        json.dumps(
            {
                "type": "NAVER_SESSION_RENEW",
                "result": result
            }
        )
    )

    return result
