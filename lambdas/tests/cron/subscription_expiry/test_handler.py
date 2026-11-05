import importlib
import json
from datetime import UTC, datetime

import pytest
from shared import notification_dispatcher

subscription_expiry = importlib.import_module("cron.subscription_expiry")

FIXED_NOW = datetime(2026, 11, 6, 15, 5, 0, tzinfo=UTC)
PAST = "2026-11-06T00:00:00+00:00"
FUTURE = "2026-12-06T00:00:00+00:00"


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW if tz else FIXED_NOW.replace(tzinfo=None)


@pytest.fixture(autouse=True)
def ddb(mocker, monkeypatch, dynamodb_table):
    monkeypatch.setattr(subscription_expiry, "datetime", FixedDatetime)
    mocker.patch.object(subscription_expiry, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "dynamodb", dynamodb_table.client)
    return dynamodb_table


@pytest.fixture(autouse=True)
def discord(mocker):
    return mocker.patch.object(
        subscription_expiry,
        "send_message",
        return_value=mocker.Mock(status_code=200, text=""),
    )


def sent(discord):
    return {
        call.kwargs["channel_id"]: call.kwargs["data"]["embeds"][0]
        for call in discord.call_args_list
    }


REPORT_CHANNEL = "1"
ERROR_CHANNEL = "2"


@pytest.fixture(autouse=True)
def channels(monkeypatch):
    monkeypatch.setattr(
        subscription_expiry,
        "DISCORD_SUBSCRIPTION_EXPIRY_REPORT_CHANNEL_ID",
        REPORT_CHANNEL,
    )
    monkeypatch.setattr(
        subscription_expiry,
        "DISCORD_SUBSCRIPTION_EXPIRY_ERROR_CHANNEL_ID",
        ERROR_CHANNEL,
    )


def put_guild(table, guild_id="1", max_limit=250):
    table.put_item(
        Item={
            "PK": f"GUILD#{guild_id}",
            "SK": f"GUILD#{guild_id}",
            "type": "GUILD",
            "guild_id": guild_id,
            "max_limit": max_limit,
            "current_count": 3,
        }
    )


def put_subscription(table, guild_id="1", expires_at=PAST, status="ACTIVE"):
    table.put_item(
        Item={
            "PK": f"GUILD#{guild_id}",
            "SK": "SUB#CURRENT",
            "type": "SUBSCRIPTION",
            "guild_id": guild_id,
            "plan_type": "MONTHLY_SUB_2000",
            "status": status,
            "expires_at": expires_at,
        }
    )


def put_order(table, sk, product_type, guild_id="1", added=None, status="SUCCESS"):
    slot_info = {"previous_slot": 5, "final_slot": 250}
    if added is not None:
        slot_info = {"previous_slot": 5, "added_slot": added, "final_slot": 5 + added}
    table.put_item(
        Item={
            "PK": f"GUILD#{guild_id}",
            "SK": f"ORDER#{sk}",
            "type": "ORDER",
            "guild_id": guild_id,
            "product_type": product_type,
            "payment_status": status,
            "slot_info": slot_info,
        }
    )


def put_noti(table, channel_id, guild_id="1"):
    table.put_item(
        Item={
            "PK": "CHZZK#abc",
            "SK": f"NOTI#{channel_id}",
            "type": "NOTI",
            "guild_id": guild_id,
            "is_subscription_active": True,
        }
    )


def get_item(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk}).get("Item")


def run():
    return subscription_expiry.handler({}, None)


def test_expires_subscription_and_restores_guild(ddb):
    put_guild(ddb.table)
    put_subscription(ddb.table)
    put_order(ddb.table, "20260101000000#a", "SLOT_5", added=5)
    put_order(ddb.table, "20260102000000#b", "SLOT_10", added=10)
    put_order(ddb.table, "20260201000000#c", "MONTHLY_SUB_2000")
    put_noti(ddb.table, "10")
    put_noti(ddb.table, "20", guild_id="2")

    result = run()

    assert result == {"expired": ["1"], "skipped": [], "failed": []}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "EXPIRED"
    guild = get_item(ddb.table, "GUILD#1", "GUILD#1")
    assert guild["max_limit"] == 20
    assert guild["current_count"] == 3
    assert (
        get_item(ddb.table, "CHZZK#abc", "NOTI#10")["is_subscription_active"] is False
    )
    assert get_item(ddb.table, "CHZZK#abc", "NOTI#20")["is_subscription_active"] is True


def test_guild_without_slot_orders_returns_to_default(ddb):
    put_guild(ddb.table)
    put_subscription(ddb.table)

    run()

    assert get_item(ddb.table, "GUILD#1", "GUILD#1")["max_limit"] == 5


@pytest.mark.parametrize(
    ("expires_at", "status"),
    [(FUTURE, "ACTIVE"), (PAST, "EXPIRED"), (PAST, "SUSPENDED")],
    ids=["not-expired", "already-expired", "suspended"],
)
def test_other_subscriptions_are_left_alone(ddb, expires_at, status):
    put_guild(ddb.table)
    put_subscription(ddb.table, expires_at=expires_at, status=status)

    result = run()

    assert result == {"expired": [], "skipped": [], "failed": []}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == status
    assert get_item(ddb.table, "GUILD#1", "GUILD#1")["max_limit"] == 250


def test_subscription_renewed_after_query_is_skipped(mocker, ddb):
    put_guild(ddb.table)
    put_subscription(ddb.table, expires_at=FUTURE)
    mocker.patch.object(
        subscription_expiry,
        "query_expired_subscriptions",
        return_value=[{"guild_id": {"S": "1"}, "expires_at": {"S": PAST}}],
    )

    result = run()

    assert result == {"expired": [], "skipped": ["1"], "failed": []}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "ACTIVE"
    assert get_item(ddb.table, "GUILD#1", "GUILD#1")["max_limit"] == 250


def test_missing_guild_item_is_skipped_without_creating_it(ddb):
    put_subscription(ddb.table)

    result = run()

    assert result["skipped"] == ["1"]
    assert get_item(ddb.table, "GUILD#1", "GUILD#1") is None
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "ACTIVE"


def test_one_failure_does_not_stop_others(mocker, ddb):
    for guild_id in ("1", "2"):
        put_guild(ddb.table, guild_id=guild_id)
        put_subscription(ddb.table, guild_id=guild_id)
    original = subscription_expiry.query_orders

    def flaky(guild_id):
        if guild_id == "1":
            raise RuntimeError("boom")
        return original(guild_id)

    mocker.patch.object(subscription_expiry, "query_orders", side_effect=flaky)

    result = run()

    assert result == {"expired": ["2"], "skipped": [], "failed": ["1"]}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "ACTIVE"
    assert get_item(ddb.table, "GUILD#2", "SUB#CURRENT")["status"] == "EXPIRED"


def test_noti_deactivation_failure_is_reported(mocker, ddb):
    put_guild(ddb.table)
    put_subscription(ddb.table)
    mocker.patch.object(
        subscription_expiry,
        "deactivate_subscription_for_guild",
        side_effect=RuntimeError("boom"),
    )

    result = run()

    assert result == {"expired": [], "skipped": [], "failed": ["1"]}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "EXPIRED"


def order(product_type, added=None, status="SUCCESS"):
    item = {
        "product_type": {"S": product_type},
        "payment_status": {"S": status},
        "slot_info": {"M": {}},
    }
    if added is not None:
        item["slot_info"]["M"]["added_slot"] = {"N": str(added)}
    return item


@pytest.mark.parametrize(
    ("orders", "expected"),
    [
        ([], 5),
        ([order("SLOT_5", 5), order("SLOT_10", 10)], 20),
        ([order("MONTHLY_SUB_2000")], 5),
        ([order("SLOT_5", 5, status="FAILED")], 5),
        ([order("SLOT_5")], 5),
    ],
    ids=["none", "slots", "subscription-only", "failed-payment", "no-added-slot"],
)
def test_restored_max_limit(orders, expected):
    assert subscription_expiry.restored_max_limit(orders) == expected


class TestDiscordMessages:
    def test_report_lists_expired_guilds(self, ddb, discord):
        put_guild(ddb.table)
        put_subscription(ddb.table)

        run()

        assert discord.call_count == 1
        call = discord.call_args
        assert call.kwargs["token"] == subscription_expiry.ADMIN_DISCORD_TOKEN
        embed = call.kwargs["data"]["embeds"][0]
        assert call.kwargs["channel_id"] == REPORT_CHANNEL
        assert embed["title"] == "SUBSCRIPTION_EXPIRY_REPORT"
        assert embed["description"] == (
            "✅ `1` 만료 (2026-11-06 09:00:00 KST), 슬롯 5개로 복원"
        )

    def test_nothing_is_sent_without_expired_subscriptions(self, ddb, discord):
        put_subscription(ddb.table, expires_at=FUTURE)

        run()

        assert discord.call_count == 0

    def test_skipped_guild_is_reported(self, ddb, discord):
        put_subscription(ddb.table)

        run()

        assert sent(discord)[REPORT_CHANNEL]["description"] == (
            "⏭️ `1` 건너뜀 (None, ConditionalCheckFailed)"
        )

    def test_failures_go_to_error_channel(self, mocker, ddb, discord):
        put_guild(ddb.table)
        put_subscription(ddb.table)
        mocker.patch.object(
            subscription_expiry, "query_orders", side_effect=RuntimeError("boom")
        )

        run()

        messages = sent(discord)
        assert REPORT_CHANNEL not in messages
        assert messages[ERROR_CHANNEL]["title"] == "SUBSCRIPTION_EXPIRY_ERROR"
        assert messages[ERROR_CHANNEL]["description"] == ("`1` 만료 처리 실패: `boom`")

    def test_noti_failure_is_reported_on_both_channels(self, mocker, ddb, discord):
        put_guild(ddb.table)
        put_subscription(ddb.table)
        put_guild(ddb.table, guild_id="2")
        put_subscription(ddb.table, guild_id="2")
        original = subscription_expiry.deactivate_subscription_for_guild

        def flaky(guild_id):
            if guild_id == "1":
                raise RuntimeError("boom")
            original(guild_id)

        mocker.patch.object(
            subscription_expiry, "deactivate_subscription_for_guild", side_effect=flaky
        )

        run()

        messages = sent(discord)
        assert "`2` 만료" in messages[REPORT_CHANNEL]["description"]
        assert messages[ERROR_CHANNEL]["description"] == (
            "`1` 구독은 만료됐지만 알림 플래그 해제 실패 (수동 확인 필요): `boom`"
        )

    def test_query_failure_alerts_and_raises(self, mocker, discord):
        mocker.patch.object(
            subscription_expiry,
            "query_expired_subscriptions",
            side_effect=RuntimeError("boom"),
        )

        with pytest.raises(RuntimeError):
            run()

        assert sent(discord)[ERROR_CHANNEL]["description"] == (
            "만료된 구독 조회 실패: `boom`"
        )

    def test_discord_failure_is_logged(self, mocker, ddb, discord):
        put_guild(ddb.table)
        put_subscription(ddb.table)
        discord.return_value = mocker.Mock(status_code=500, text="oops")
        error = mocker.patch.object(subscription_expiry.logger, "error")

        result = run()

        assert result["expired"] == ["1"]
        logged = json.loads(error.call_args.args[0])
        assert logged == {
            "type": "DISCORD_MESSAGE_SEND_ERROR",
            "channel_id": REPORT_CHANNEL,
            "status_code": 500,
            "text": "oops",
        }
