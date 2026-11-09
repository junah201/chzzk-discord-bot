import importlib
import json

import pytest
from shared import notification_dispatcher

sync_guild_slots = importlib.import_module("api.guilds.sync_guild_slots")

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(sync_guild_slots, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "dynamodb", dynamodb_table.client)
    return dynamodb_table


def call(guild_id=GUILD_ID):
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "pathParameters": {"guild_id": guild_id},
    }
    res = sync_guild_slots.handler(event, None)
    return res, json.loads(res["body"])


def put_guild(table, **attrs):
    table.put_item(
        Item={
            "PK": f"GUILD#{GUILD_ID}",
            "SK": f"GUILD#{GUILD_ID}",
            "type": "GUILD",
            "guild_id": GUILD_ID,
            **attrs,
        }
    )


def put_noti(table, channel_id, guild_id=GUILD_ID):
    table.put_item(
        Item={
            "PK": "CHZZK#abc",
            "SK": f"NOTI#{channel_id}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": channel_id,
        }
    )


def get_guild(table):
    key = f"GUILD#{GUILD_ID}"
    return table.get_item(Key={"PK": key, "SK": key}).get("Item")


def test_out_of_sync_count_is_fixed(ddb):
    put_guild(ddb.table, current_count=5, max_limit=10)
    put_noti(ddb.table, "10")
    put_noti(ddb.table, "11")
    put_noti(ddb.table, "20", guild_id="2")

    res, body = call()

    assert res["statusCode"] == 200
    assert body == {"current_count": 2, "previous_count": 5, "max_limit": 10}
    guild = get_guild(ddb.table)
    assert guild["current_count"] == 2
    assert guild["max_limit"] == 10


def test_in_sync_count_is_left_alone(mocker, ddb):
    put_guild(ddb.table, current_count=1, max_limit=10)
    put_noti(ddb.table, "10")
    update_item = mocker.spy(ddb.client, "update_item")

    _, body = call()

    assert body == {"current_count": 1, "previous_count": 1, "max_limit": 10}
    assert update_item.call_count == 0


def test_missing_guild_item_is_created_with_real_count(ddb):
    put_noti(ddb.table, "10")

    _, body = call()

    assert body == {"current_count": 1, "previous_count": 0, "max_limit": 5}
    guild = get_guild(ddb.table)
    assert guild["current_count"] == 1
    assert guild["guild_id"] == GUILD_ID
    assert guild["type"] == "GUILD"
    assert "max_limit" not in guild


def test_empty_guild_needs_no_write(mocker, ddb):
    update_item = mocker.spy(ddb.client, "update_item")

    _, body = call()

    assert body == {"current_count": 0, "previous_count": 0, "max_limit": 5}
    assert update_item.call_count == 0
    assert get_guild(ddb.table) is None


def test_non_admin_is_rejected(as_admin):
    as_admin.return_value = False

    res, _ = call()

    assert res["statusCode"] == 403
