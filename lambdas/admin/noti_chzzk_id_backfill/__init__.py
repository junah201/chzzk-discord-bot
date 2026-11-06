import json
import logging

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from shared import middleware
from shared.utils import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table = boto3.resource("dynamodb").Table("chzzk-bot-db")

CHZZK_PREFIX = "CHZZK#"


def parse_dry_run(event) -> bool:
    event = event if isinstance(event, dict) else {}
    value = event.get("dry_run", True)
    if not isinstance(value, bool):
        raise ValueError("'dry_run' must be a boolean")
    return value


def scan_notis_without_chzzk_id():
    kwargs = {
        "FilterExpression": Attr("type").eq("NOTI") & Attr("chzzk_id").not_exists(),
        "ProjectionExpression": "PK, SK",
    }
    while True:
        res = table.scan(**kwargs)
        yield from res.get("Items", [])
        last_key = res.get("LastEvaluatedKey")
        if last_key is None:
            return
        kwargs["ExclusiveStartKey"] = last_key


def backfill(item) -> bool:
    try:
        table.update_item(
            Key={"PK": item["PK"], "SK": item["SK"]},
            UpdateExpression="SET chzzk_id = :chzzk_id",
            ConditionExpression=Attr("PK").exists() & Attr("chzzk_id").not_exists(),
            ExpressionAttributeValues={
                ":chzzk_id": item["PK"].removeprefix(CHZZK_PREFIX)
            },
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


@middleware(logger)
def handler(event, _context):
    dry_run = parse_dry_run(event)

    found = []
    skipped = []
    updated = 0
    for item in scan_notis_without_chzzk_id():
        if not item["PK"].startswith(CHZZK_PREFIX):
            skipped.append(item["PK"])
            continue
        found.append(item)
        if not dry_run and backfill(item):
            updated += 1

    summary = {
        "type": "NOTI_CHZZK_ID_BACKFILL",
        "dry_run": dry_run,
        "found": len(found),
        "updated": updated,
        "skipped_pks": skipped,
        "sample": [{"PK": i["PK"], "SK": i["SK"]} for i in found[:20]],
    }
    logger.info(json.dumps(summary, ensure_ascii=False))

    return build_response(200, data=summary)
