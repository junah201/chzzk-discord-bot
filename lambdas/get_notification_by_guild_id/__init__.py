import json
import logging

import boto3

from shared import dynamo_to_python, middleware

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    res = dynamodb.query(
        TableName="chzzk-bot-db",
        IndexName="GSI-GuildID-v2",
        KeyConditionExpression="guild_id = :guild_id",
        ExpressionAttributeValues={":guild_id": {"S": f"{guild_id}"}},
    )

    result = [dynamo_to_python(item) for item in res.get("Items", [])]

    return {"statusCode": 200, "body": json.dumps(result)}
