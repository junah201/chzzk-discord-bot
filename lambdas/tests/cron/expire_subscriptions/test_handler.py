import importlib
import json
from datetime import UTC, datetime

import pytest
from shared import notification_dispatcher

expire_subscriptions = importlib.import_module("cron.expire_subscriptions")

FIXED_NOW = datetime(2026, 11, 6, 15, 5, 0, tzinfo=UTC)
PAST = "2026-11-06T00:00:00+00:00"
FUTURE = "2026-12-06T00:00:00+00:00"


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW if tz else FIXED_NOW.replace(tzinfo=None)


@pytest.fixture(autouse=True)
def ddb(mocker, monkeypatch, dynamodb_table):
    monkeypatch.setattr(expire_subscriptions, "datetime", FixedDatetime)
    mocker.patch.object(expire_subscriptions, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "dynamodb", dynamodb_table.client)
    return dynamodb_table


@pytest.fixture(autouse=True)
def discord(mocker):
    return mocker.patch.object(
        expire_subscriptions,
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
        expire_subscriptions,
        "DISCORD_SUBSCRIPTION_EXPIRY_REPORT_CHANNEL_ID",
        REPORT_CHANNEL,
    )
    monkeypatch.setattr(
        expire_subscriptions,
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


def put_subscription(
    table, guild_id="1", expires_at=PAST, status="ACTIVE", previous_slot=5
):
    """SUB#CURRENT와 그 구독을 시작한 주문을 함께 저장한다. previous_slot=None이면 주문은 없다."""
    if previous_slot is not None:
        put_order(
            table, "20261006000000#sub", "MONTHLY_SUB_2000", guild_id, previous_slot
        )
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


def put_order(table, sk, product_type, guild_id="1", previous_slot=5, status="SUCCESS"):
    if product_type == "MONTHLY_SUB_2000":
        slot_info = {"previous_slot": previous_slot, "final_slot": 250}
    else:
        slot_info = {
            "previous_slot": previous_slot,
            "added_slot": 5,
            "final_slot": previous_slot + 5,
        }
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
    return expire_subscriptions.handler({}, None)


def test_expires_subscription_and_restores_guild(ddb):
    put_guild(ddb.table)
    # 유료화 이전 가입 서버(15)가 슬롯 5개를 산 뒤 구독하고 한 번 갱신했다.
    put_order(ddb.table, "20260101000000#a", "SLOT_5", previous_slot=15)
    put_subscription(ddb.table, previous_slot=None)
    put_order(ddb.table, "20260201000000#b", "MONTHLY_SUB_2000", previous_slot=20)
    put_order(ddb.table, "20260301000000#c", "MONTHLY_SUB_2000", previous_slot=250)
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


def test_guild_without_subscription_order_is_not_touched(ddb, discord):
    put_guild(ddb.table)
    put_subscription(ddb.table, previous_slot=None)

    result = run()

    assert result == {"expired": [], "skipped": [], "failed": ["1"]}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "ACTIVE"
    assert get_item(ddb.table, "GUILD#1", "GUILD#1")["max_limit"] == 250
    assert (
        "구독 전 슬롯 한도를 알 수 있는 구독 주문이 없습니다"
        in (discord.call_args.kwargs["data"]["embeds"][0]["description"])
    )


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
        expire_subscriptions,
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
    original = expire_subscriptions.query_orders

    def flaky(guild_id):
        if guild_id == "1":
            raise RuntimeError("boom")
        return original(guild_id)

    mocker.patch.object(expire_subscriptions, "query_orders", side_effect=flaky)

    result = run()

    assert result == {"expired": ["2"], "skipped": [], "failed": ["1"]}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "ACTIVE"
    assert get_item(ddb.table, "GUILD#2", "SUB#CURRENT")["status"] == "EXPIRED"


def test_noti_deactivation_failure_is_reported(mocker, ddb):
    put_guild(ddb.table)
    put_subscription(ddb.table)
    mocker.patch.object(
        expire_subscriptions,
        "deactivate_subscription_for_guild",
        side_effect=RuntimeError("boom"),
    )

    result = run()

    assert result == {"expired": [], "skipped": [], "failed": ["1"]}
    assert get_item(ddb.table, "GUILD#1", "SUB#CURRENT")["status"] == "EXPIRED"


def order(sk, previous_slot, product_type="MONTHLY_SUB_2000", status="SUCCESS"):
    item = {
        "SK": {"S": f"ORDER#{sk}"},
        "product_type": {"S": product_type},
        "payment_status": {"S": status},
        "slot_info": {"M": {}},
    }
    if previous_slot is not None:
        item["slot_info"]["M"]["previous_slot"] = {"N": str(previous_slot)}
    return item


@pytest.mark.parametrize(
    ("orders", "expected"),
    [
        ([order("1", 5)], 5),
        ([order("1", 15)], 15),
        ([order("1", 15), order("2", 250), order("3", 250)], 15),
        ([order("3", 250), order("1", 5), order("2", 20)], 20),
        ([order("1", 5), order("2", 20, status="FAILED")], 5),
        ([order("1", 5), order("2", 10, product_type="SLOT_5")], 5),
        ([order("1", 5), order("2", None)], 5),
    ],
    ids=[
        "new-guild",
        "legacy-guild",
        "renewals-skipped",
        "latest-by-sk",
        "failed-payment",
        "slot-order-ignored",
        "missing-previous-slot",
    ],
)
def test_restored_max_limit(orders, expected):
    assert expire_subscriptions.restored_max_limit(orders) == expected


@pytest.mark.parametrize(
    "orders",
    [[], [order("1", 250)], [order("1", 5, product_type="SLOT_5")]],
    ids=["none", "only-renewals", "only-slot-orders"],
)
def test_restored_max_limit_unknown(orders):
    with pytest.raises(expire_subscriptions.UnknownSlotLimitError):
        expire_subscriptions.restored_max_limit(orders)


class TestDiscordMessages:
    def test_report_lists_expired_guilds(self, ddb, discord):
        put_guild(ddb.table)
        put_subscription(ddb.table)

        run()

        assert discord.call_count == 1
        call = discord.call_args
        assert call.kwargs["token"] == expire_subscriptions.ADMIN_DISCORD_TOKEN
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
            expire_subscriptions, "query_orders", side_effect=RuntimeError("boom")
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
        original = expire_subscriptions.deactivate_subscription_for_guild

        def flaky(guild_id):
            if guild_id == "1":
                raise RuntimeError("boom")
            original(guild_id)

        mocker.patch.object(
            expire_subscriptions, "deactivate_subscription_for_guild", side_effect=flaky
        )

        run()

        messages = sent(discord)
        assert "`2` 만료" in messages[REPORT_CHANNEL]["description"]
        assert messages[ERROR_CHANNEL]["description"] == (
            "`1` 구독은 만료됐지만 알림 플래그 해제 실패 (수동 확인 필요): `boom`"
        )

    def test_query_failure_alerts_and_raises(self, mocker, discord):
        mocker.patch.object(
            expire_subscriptions,
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
        error = mocker.patch.object(expire_subscriptions.logger, "error")

        result = run()

        assert result["expired"] == ["1"]
        logged = json.loads(error.call_args.args[0])
        assert logged == {
            "type": "DISCORD_MESSAGE_SEND_ERROR",
            "channel_id": REPORT_CHANNEL,
            "status_code": 500,
            "text": "oops",
        }
