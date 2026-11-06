import importlib
import json

import pytest
from botocore.exceptions import ClientError

delete_notification = importlib.import_module("api.notifications.delete_notification")

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"
CHANNEL_ID = "10"
CHZZK_ID = "abc"


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(delete_notification, "dynamodb", dynamodb_table.client)
    return dynamodb_table


def call(**body):
    payload = {"chzzk_id": CHZZK_ID, "guild_id": GUILD_ID, "channel_id": CHANNEL_ID}
    payload.update(body)
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "body": json.dumps({k: v for k, v in payload.items() if v is not None}),
    }
    res = delete_notification.handler(event, None)
    return res, json.loads(res["body"]) if "body" in res else None


def put_guild(table, current_count=1, guild_id=GUILD_ID):
    item = {
        "PK": f"GUILD#{guild_id}",
        "SK": f"GUILD#{guild_id}",
        "type": "GUILD",
        "guild_id": guild_id,
        "max_limit": 5,
    }
    if current_count is not None:
        item["current_count"] = current_count
    table.put_item(Item=item)


def put_noti(table, guild_id=GUILD_ID, channel_id=CHANNEL_ID):
    table.put_item(
        Item={
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"NOTI#{channel_id}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": channel_id,
        }
    )


def get_noti(table, channel_id=CHANNEL_ID):
    return table.get_item(
        Key={"PK": f"CHZZK#{CHZZK_ID}", "SK": f"NOTI#{channel_id}"}
    ).get("Item")


def get_count(table, guild_id=GUILD_ID):
    item = table.get_item(
        Key={"PK": f"GUILD#{guild_id}", "SK": f"GUILD#{guild_id}"}
    ).get("Item")
    return item.get("current_count") if item else None


def test_deletes_notification_and_decrements_count(ddb):
    put_guild(ddb.table, current_count=3)
    put_noti(ddb.table)
    put_noti(ddb.table, channel_id="11")

    res, body = call()

    assert res["statusCode"] == 204
    assert body is None
    assert get_noti(ddb.table) is None
    assert get_noti(ddb.table, "11") is not None
    assert get_count(ddb.table) == 2


def test_last_notification_brings_count_to_zero(ddb):
    put_guild(ddb.table, current_count=1)
    put_noti(ddb.table)

    res, _ = call()

    assert res["statusCode"] == 204
    assert get_count(ddb.table) == 0


@pytest.mark.parametrize("missing", ["chzzk_id", "guild_id", "channel_id"])
def test_missing_field_is_400(ddb, missing):
    put_guild(ddb.table)
    put_noti(ddb.table)

    res, body = call(**{missing: None})

    assert res["statusCode"] == 400
    assert body["code"] == "INVALID_REQUEST"
    assert get_noti(ddb.table) is not None


def test_missing_notification_is_404(ddb):
    put_guild(ddb.table, current_count=1)

    res, body = call()

    assert res["statusCode"] == 404
    assert body["code"] == "NOTIFICATION_NOT_FOUND"
    assert get_count(ddb.table) == 1


def test_notification_of_other_guild_is_404_and_kept(ddb):
    put_guild(ddb.table, current_count=1)
    put_guild(ddb.table, current_count=1, guild_id="2")
    put_noti(ddb.table, guild_id="2")

    res, _ = call()

    assert res["statusCode"] == 404
    assert get_noti(ddb.table)["guild_id"] == "2"
    assert get_count(ddb.table) == 1
    assert get_count(ddb.table, "2") == 1


@pytest.mark.parametrize(
    "current_count", [0, None], ids=["count-zero", "count-missing"]
)
def test_out_of_sync_count_blocks_delete(ddb, current_count):
    # 현재 동작: current_count가 0이거나 없으면(카운트 불일치) 알림이 있어도 삭제되지 않고 404가 된다.
    put_guild(ddb.table, current_count=current_count)
    put_noti(ddb.table)

    res, _ = call()

    assert res["statusCode"] == 404
    assert get_noti(ddb.table) is not None


def test_missing_guild_item_blocks_delete(ddb):
    # 현재 동작: GUILD 항목이 없으면 알림이 있어도 삭제되지 않고 404가 된다.
    put_noti(ddb.table)

    res, _ = call()

    assert res["statusCode"] == 404
    assert get_noti(ddb.table) is not None


def test_other_dynamodb_error_is_500(mocker, ddb):
    log_error = mocker.patch.object(delete_notification.logger, "error")
    mocker.patch.object(
        ddb.client,
        "transact_write_items",
        side_effect=ClientError(
            {"Error": {"Code": "ProvisionedThroughputExceededException"}},
            "TransactWriteItems",
        ),
    )

    res, body = call()

    assert res["statusCode"] == 500
    assert body["message"] == "서버 오류가 발생했습니다."
    assert (
        json.loads(log_error.call_args.args[0])["type"] == "DELETE_NOTIFICATION_ERROR"
    )


def test_transaction_canceled_without_condition_failure_is_500(mocker, ddb):
    mocker.patch.object(delete_notification.logger, "error")
    mocker.patch.object(
        ddb.client,
        "transact_write_items",
        side_effect=ClientError(
            {
                "Error": {"Code": "TransactionCanceledException"},
                "CancellationReasons": [
                    {"Code": "None"},
                    {"Code": "TransactionConflict"},
                ],
            },
            "TransactWriteItems",
        ),
    )

    res, _ = call()

    assert res["statusCode"] == 500
