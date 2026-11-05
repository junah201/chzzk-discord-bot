import boto3
from bot.admin_event_handler.purchase import Purchase

TABLE_NAME = "chzzk-bot-db"

dynamodb = boto3.client("dynamodb")
table = boto3.resource("dynamodb").Table(TABLE_NAME)


def get_guild(guild_id: str) -> dict | None:
    guild_pk = f"GUILD#{guild_id}"
    return table.get_item(Key={"PK": guild_pk, "SK": guild_pk}).get("Item")


def save_purchase(guild_id: str, purchase: Purchase) -> None:
    """주문 기록, (구독이면) 구독 정보, 길드 max_limit을 한 트랜잭션으로 저장합니다."""
    guild_pk = f"GUILD#{guild_id}"
    items = [
        {
            "Put": {
                "TableName": TABLE_NAME,
                "Item": purchase.order_item,
                "ConditionExpression": "attribute_not_exists(SK)",
            }
        }
    ]
    if purchase.subscription_item is not None:
        items.append(
            {"Put": {"TableName": TABLE_NAME, "Item": purchase.subscription_item}}
        )
    items.append(
        {
            "Update": {
                "TableName": TABLE_NAME,
                "Key": {"PK": {"S": guild_pk}, "SK": {"S": guild_pk}},
                "UpdateExpression": "SET max_limit = :max_limit",
                "ExpressionAttributeValues": {
                    ":max_limit": {"N": str(purchase.new_max_limit)}
                },
            }
        }
    )
    dynamodb.transact_write_items(TransactItems=items)


def set_current_count(guild_id: str, count: int) -> None:
    guild_pk = f"GUILD#{guild_id}"
    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"PK": {"S": guild_pk}, "SK": {"S": guild_pk}},
        UpdateExpression="SET current_count = :real_count",
        ExpressionAttributeValues={":real_count": {"N": str(count)}},
    )
