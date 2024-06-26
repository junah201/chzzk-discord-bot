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
    items.sort(key=lambda x: x.get("PK"))

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
        try:
            NEW_NID_SES = res.headers["set-cookie"].split("NID_SES=")[
                1].split(";")[0]
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "NAVER_SESSION_RENEW_ERROR",
                        "PK": item.get("PK"),
                        "error": str(e),
                        "text": res.text
                    }
                )
            )
            NEW_NID_SES = "error"

        if NEW_NID_SES not in ["expired", "error"]:
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
            "NID_AUT": NID_AUT,
            "ORIGINAL_NID_SES": f"{NID_SES[:7]}...{NID_SES[-7:]}",
            "NEW_NID_SES": f"{NEW_NID_SES[:7]}...{NEW_NID_SES[-7:]}" if NEW_NID_SES not in ["expired", "error"] else NEW_NID_SES
        })
        time.sleep(2)

    logger.info(
        json.dumps(
            {
                "type": "NAVER_SESSION_RENEW",
                "result": result
            }
        )
    )

    return result
