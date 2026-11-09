import boto3
from shared import dynamo_to_python, middleware
from shared.event import get_path_param
from shared.utils import build_response

dynamodb = boto3.client("dynamodb")


INTERNAL_KEYS = ("PK", "SK", "type")


@middleware(require_guild_admin=True)
def handler(event, _context):
    guild_id = get_path_param(event, "guild_id")

    res = dynamodb.query(
        TableName="chzzk-bot-db",
        IndexName="GSI-GuildID-v2",
        KeyConditionExpression="guild_id = :guild_id",
        FilterExpression="#type = :type_val",
        ExpressionAttributeNames={
            "#type": "type",
        },
        ExpressionAttributeValues={
            ":guild_id": {"S": str(guild_id)},
            ":type_val": {"S": "NOTI"},
        },
    )

    result = [
        {k: v for k, v in dynamo_to_python(item).items() if k not in INTERNAL_KEYS}
        for item in res.get("Items", [])
    ]

    return build_response(200, data=result)
