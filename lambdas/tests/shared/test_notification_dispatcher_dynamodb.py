import json
from datetime import UTC, datetime

import pytest
from shared import notification_dispatcher
from shared.notification_dispatcher import (
    activate_subscription_for_guild,
    is_guild_subscription_active,
)

FIXED_NOW = datetime(2026, 11, 1, 12, 0, 0, 123456, tzinfo=UTC)


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW if tz is None else FIXED_NOW.astimezone(tz)


@pytest.fixture(autouse=True)
def use_dynamodb(mocker, dynamodb_table):
    mocker.patch.object(notification_dispatcher, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "table", dynamodb_table.table)
    return dynamodb_table


@pytest.fixture(autouse=True)
def fixed_now(monkeypatch):
    monkeypatch.setattr(notification_dispatcher, "datetime", FixedDatetime)


def put_subscription(table, guild_id="1", **attrs):
    item = {
        "PK": f"GUILD#{guild_id}",
        "SK": "SUB#CURRENT",
        "type": "SUBSCRIPTION",
        "guild_id": guild_id,
        "plan_type": "MONTHLY_SUB_2000",
        "status": "ACTIVE",
        "expires_at": "2026-12-01T12:00:00.123456+00:00",
        **attrs,
    }
    item = {k: v for k, v in item.items() if v is not None}
    table.put_item(Item=item)


class TestIsGuildSubscriptionActive:
    def test_no_subscription(self):
        assert is_guild_subscription_active("1") is False

    def test_active_and_not_expired(self, use_dynamodb):
        put_subscription(use_dynamodb.table)

        assert is_guild_subscription_active("1") is True

    def test_int_guild_id_is_converted(self, use_dynamodb):
        put_subscription(use_dynamodb.table)

        assert is_guild_subscription_active(1) is True

    def test_other_guild_subscription_does_not_count(self, use_dynamodb):
        put_subscription(use_dynamodb.table, guild_id="2")

        assert is_guild_subscription_active("1") is False

    @pytest.mark.parametrize(
        "expires_at",
        [
            "2026-11-01T11:59:59.999999+00:00",
            "2026-11-01T12:00:00.123456+00:00",
            "2025-12-01T12:00:00+00:00",
        ],
        ids=["just-expired", "expires-now", "last-year"],
    )
    def test_expired(self, use_dynamodb, expires_at):
        put_subscription(use_dynamodb.table, expires_at=expires_at)

        assert is_guild_subscription_active("1") is False

    def test_expires_one_microsecond_later(self, use_dynamodb):
        put_subscription(
            use_dynamodb.table, expires_at="2026-11-01T12:00:00.123457+00:00"
        )

        assert is_guild_subscription_active("1") is True

    @pytest.mark.parametrize("status", ["EXPIRED", "SUSPENDED", "active", ""])
    def test_non_active_status(self, use_dynamodb, status):
        put_subscription(use_dynamodb.table, status=status)

        assert is_guild_subscription_active("1") is False

    def test_missing_status(self, use_dynamodb):
        put_subscription(use_dynamodb.table, status=None)

        assert is_guild_subscription_active("1") is False

    # GSI-Type-ExpiresAt의 키라서 빈 문자열 expires_at은 저장할 수 없다.
    def test_missing_expires_at_is_inactive_and_warned(self, mocker, use_dynamodb):
        warning = mocker.patch.object(notification_dispatcher.logger, "warning")
        put_subscription(use_dynamodb.table, expires_at=None)

        assert is_guild_subscription_active("1") is False
        assert json.loads(warning.call_args.args[0]) == {
            "type": "SUBSCRIPTION_EXPIRES_AT_MISSING",
            "guild_id": "1",
        }

    def test_dynamodb_error_is_inactive_and_logged(self, mocker, use_dynamodb):
        error = mocker.patch.object(notification_dispatcher.logger, "error")
        mocker.patch.object(
            use_dynamodb.table, "get_item", side_effect=RuntimeError("boom")
        )

        assert is_guild_subscription_active("1") is False
        assert json.loads(error.call_args.args[0]) == {
            "type": "SUBSCRIPTION_CHECK_ERROR",
            "guild_id": "1",
            "error": "boom",
        }


class TestExpiresAtStringComparison:
    """expires_at은 ISO 문자열 그대로 비교한다. 관리자 봇은 datetime.now(UTC).isoformat()으로 저장한다."""

    @pytest.mark.parametrize(
        ("expires_at", "expected"),
        [
            ("2026-11-01T12:00:01+00:00", True),
            ("2026-11-01T11:59:59+00:00", False),
            ("2026-11-02T00:00:00Z", True),
            ("2026-11-01T11:00:00Z", False),
        ],
        ids=[
            "no-microseconds-future",
            "no-microseconds-past",
            "z-suffix-future",
            "z-suffix-past",
        ],
    )
    def test_utc_formats_compare_correctly(self, use_dynamodb, expires_at, expected):
        put_subscription(use_dynamodb.table, expires_at=expires_at)

        assert is_guild_subscription_active("1") is expected

    def test_non_utc_offset_is_compared_as_text(self, use_dynamodb):
        # 현재 동작: 오프셋을 계산하지 않고 문자열로 비교한다.
        # 2026-11-01T20:00:00+09:00은 UTC 11:00으로 이미 만료됐지만 활성으로 판단한다.
        put_subscription(use_dynamodb.table, expires_at="2026-11-01T20:00:00+09:00")

        assert is_guild_subscription_active("1") is True


def put_item(table, pk, sk, item_type, guild_id=None, **attrs):
    item = {"PK": pk, "SK": sk, "type": item_type, **attrs}
    if guild_id is not None:
        item["guild_id"] = guild_id
    table.put_item(Item=item)


def put_noti(table, chzzk_id, channel_id, guild_id):
    put_item(
        table,
        f"CHZZK#{chzzk_id}",
        f"NOTI#{channel_id}",
        "NOTI",
        guild_id=guild_id,
        channel_id=channel_id,
    )


def get(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk})["Item"]


class TestActivateSubscriptionForGuild:
    def test_marks_only_guild_notifications(self, use_dynamodb):
        table = use_dynamodb.table
        put_item(table, "GUILD#1", "GUILD#1", "GUILD", guild_id="1", current_count=2)
        put_subscription(table)
        put_item(table, "GUILD#1", "ORDER#20261101#abc", "ORDER", guild_id="1")
        put_noti(table, "a", "10", "1")
        put_noti(table, "b", "11", "1")
        put_noti(table, "a", "20", "2")

        activate_subscription_for_guild("1")

        assert get(table, "CHZZK#a", "NOTI#10")["is_subscription_active"] is True
        assert get(table, "CHZZK#b", "NOTI#11")["is_subscription_active"] is True
        assert "is_subscription_active" not in get(table, "CHZZK#a", "NOTI#20")
        for sk in ("GUILD#1", "SUB#CURRENT", "ORDER#20261101#abc"):
            assert "is_subscription_active" not in get(table, "GUILD#1", sk)

    def test_guild_without_items_does_nothing(self, mocker, use_dynamodb):
        update_item = mocker.spy(use_dynamodb.client, "update_item")

        activate_subscription_for_guild("1")

        update_item.assert_not_called()

    def test_follows_pagination(self, mocker, use_dynamodb):
        def noti(channel_id):
            return {
                "PK": {"S": "CHZZK#a"},
                "SK": {"S": f"NOTI#{channel_id}"},
                "type": {"S": "NOTI"},
            }

        query = mocker.patch.object(
            use_dynamodb.client,
            "query",
            side_effect=[
                {"Items": [noti("10")], "LastEvaluatedKey": {"k": {"S": "1"}}},
                {"Items": [noti("11"), {"type": {"S": "GUILD"}}]},
            ],
        )
        update_item = mocker.patch.object(use_dynamodb.client, "update_item")

        activate_subscription_for_guild("1")

        assert query.call_count == 2
        assert "ExclusiveStartKey" not in query.call_args_list[0].kwargs
        assert query.call_args_list[1].kwargs["ExclusiveStartKey"] == {"k": {"S": "1"}}
        assert query.call_args_list[0].kwargs["IndexName"] == "GSI-GuildID-v2"
        assert [c.kwargs["Key"]["SK"]["S"] for c in update_item.call_args_list] == [
            "NOTI#10",
            "NOTI#11",
        ]


def test_deactivate_subscription_for_guild(use_dynamodb):
    table = use_dynamodb.table
    for sk, guild_id in (("NOTI#10", "1"), ("NOTI#20", "2")):
        table.put_item(
            Item={
                "PK": "CHZZK#abc",
                "SK": sk,
                "type": "NOTI",
                "guild_id": guild_id,
                "is_subscription_active": True,
            }
        )

    notification_dispatcher.deactivate_subscription_for_guild("1")

    def flag(sk):
        item = table.get_item(Key={"PK": "CHZZK#abc", "SK": sk})["Item"]
        return item["is_subscription_active"]

    assert flag("NOTI#10") is False
    assert flag("NOTI#20") is True
