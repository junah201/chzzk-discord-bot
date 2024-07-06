import json
import boto3
import logging

from shared import middleware, dynamo_to_python

dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=True)
def handler(event, context):
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
        dynamo_to_python(item)
        for item in res.get('Items', [])
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
