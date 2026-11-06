import importlib
import json

import pytest

get_notification_by_guild_id = importlib.import_module(
    "api.notifications.get_notification_by_guild_id"
)

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(get_notification_by_guild_id, "dynamodb", dynamodb_table.client)
    return dynamodb_table


def call(guild_id=GUILD_ID):
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "pathParameters": {"guild_id": guild_id},
    }
    res = get_notification_by_guild_id.handler(event, None)
    return res, json.loads(res["body"])


def put_noti(table, channel_id, guild_id=GUILD_ID, **attrs):
    table.put_item(
        Item={
            "PK": "CHZZK#abc",
            "SK": f"NOTI#{channel_id}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": channel_id,
            "chzzk_id": "abc",
            **attrs,
        }
    )


def test_returns_only_this_guilds_notifications(ddb):
    put_noti(ddb.table, "10", noti_fail_count=2, disable_embed=True)
    put_noti(ddb.table, "20", guild_id="2")
    # 같은 GSI 파티션에 있는 GUILD/SUB 아이템은 응답에 섞이면 안 된다.
    for sk, type_ in ((f"GUILD#{GUILD_ID}", "GUILD"), ("SUB#CURRENT", "SUBSCRIPTION")):
        ddb.table.put_item(
            Item={
                "PK": f"GUILD#{GUILD_ID}",
                "SK": sk,
                "type": type_,
                "guild_id": GUILD_ID,
            }
        )

    res, body = call()

    assert res["statusCode"] == 200
    assert body == [
        {
            "guild_id": GUILD_ID,
            "channel_id": "10",
            "chzzk_id": "abc",
            "noti_fail_count": 2,
            "disable_embed": True,
        }
    ]


def test_guild_without_notifications_returns_empty_list():
    res, body = call()

    assert res["statusCode"] == 200
    assert body == []
