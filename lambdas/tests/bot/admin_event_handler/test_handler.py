import importlib
import json
from datetime import UTC, datetime

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from nacl.signing import SigningKey
from shared import INTERACTION_CALLBACK_TYPE, TYPE, notification_dispatcher

admin = importlib.import_module("bot.admin_event_handler")
service = importlib.import_module("bot.admin_event_handler.service")

SIGNING_KEY = SigningKey.generate()
ADMIN_ID = "777"
GUILD_ID = "1"
BUYER_ID = "42"
# 1월 31일 + 1개월은 2월 28일이 되어야 한다. (relativedelta의 월말 처리)
FIXED_NOW = datetime(2026, 1, 31, 15, 0, 0, tzinfo=UTC)


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW.replace(tzinfo=None) if tz is None else FIXED_NOW


@pytest.fixture(autouse=True)
def ddb(monkeypatch, mocker, dynamodb_table):
    monkeypatch.setattr(
        admin, "ADMIN_DISCORD_PUBLIC_KEY", SIGNING_KEY.verify_key.encode().hex()
    )
    monkeypatch.setattr(admin, "ADMIN_DISCORD_USER_ID", ADMIN_ID)
    monkeypatch.setattr(admin, "datetime", FixedDatetime)
    mocker.patch.object(service, "dynamodb", dynamodb_table.client)
    mocker.patch.object(service, "table", dynamodb_table.table)
    mocker.patch.object(notification_dispatcher, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "table", dynamodb_table.table)
    return dynamodb_table


def signed_event(body: dict, key: SigningKey = SIGNING_KEY) -> dict:
    raw_body = json.dumps(body)
    timestamp = "1700000000"
    signature = key.sign(f"{timestamp}{raw_body}".encode()).signature.hex()
    return {
        "headers": {
            "x-signature-ed25519": signature,
            "x-signature-timestamp": timestamp,
        },
        "body": raw_body,
    }


def call(body: dict) -> tuple[dict, dict | None]:
    res = admin.handler(signed_event(body), None)
    try:
        return res, json.loads(res["body"])
    except json.JSONDecodeError:
        return res, None


def interaction(type_, data=None, user_id=ADMIN_ID):
    return {"type": type_, "member": {"user": {"id": user_id}}, "data": data or {}}


def text_input(custom_id, value):
    return {
        "type": 18,
        "component": {"type": 4, "custom_id": custom_id, "value": value},
    }


def purchase(product, guild_id=GUILD_ID, buyer_id=BUYER_ID):
    return interaction(
        TYPE.MODAL_SUBMIT,
        {
            "custom_id": "add_subscription_modal",
            "components": [
                text_input("guild_id_input", guild_id),
                text_input("buyer_id_input", buyer_id),
                {
                    "type": 18,
                    "component": {
                        "type": 3,
                        "custom_id": "product_type_select",
                        "values": [product],
                    },
                },
            ],
        },
    )


def sync_slots(guild_id=GUILD_ID):
    return interaction(
        TYPE.MODAL_SUBMIT,
        {
            "custom_id": "sync_slots_modal",
            "components": [text_input("guild_id_input", guild_id)],
        },
    )


def put_guild(table, guild_id=GUILD_ID, **attrs):
    table.put_item(
        Item={
            "PK": f"GUILD#{guild_id}",
            "SK": f"GUILD#{guild_id}",
            "type": "GUILD",
            "guild_id": guild_id,
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


def get_item(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk}).get("Item")


def get_guild(table, guild_id=GUILD_ID):
    return get_item(table, f"GUILD#{guild_id}", f"GUILD#{guild_id}")


def get_orders(table, guild_id=GUILD_ID):
    return table.query(
        KeyConditionExpression=Key("PK").eq(f"GUILD#{guild_id}")
        & Key("SK").begins_with("ORDER#")
    )["Items"]


def content(body):
    return body["data"]["content"]


class TestSignature:
    def test_tampered_body_is_401(self, ddb):
        put_guild(ddb.table, max_limit=5)
        event = signed_event(purchase("SLOT_5"))
        event["body"] = json.dumps(purchase("SLOT_10"))

        res = admin.handler(event, None)

        assert res["statusCode"] == 401
        assert get_guild(ddb.table)["max_limit"] == 5
        assert get_orders(ddb.table) == []

    def test_signed_with_other_key_is_401(self):
        event = signed_event({"type": TYPE.PING}, key=SigningKey.generate())

        res = admin.handler(event, None)

        assert res["statusCode"] == 401

    def test_ping(self):
        res, body = call({"type": TYPE.PING})

        assert res["statusCode"] == 200
        assert body == {"type": 1}


class TestAdminOnly:
    def test_other_user_is_rejected_without_writes(self, ddb):
        put_guild(ddb.table, max_limit=5)

        res, body = call({**purchase("SLOT_10"), "member": {"user": {"id": "123"}}})

        assert res["statusCode"] == 200
        assert body["data"]["flags"] == 64
        assert "권한이 없습니다" in content(body)
        assert get_guild(ddb.table)["max_limit"] == 5
        assert get_orders(ddb.table) == []

    def test_missing_user_is_rejected(self):
        _, body = call({"type": TYPE.APPLICATION_COMMAND, "data": {"name": "구독추가"}})

        assert body["type"] == INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE
        assert "권한이 없습니다" in content(body)

    def test_admin_in_dm_uses_user_field(self):
        body = {"type": TYPE.APPLICATION_COMMAND, "data": {"name": "구독추가"}}
        body["user"] = {"id": ADMIN_ID}

        _, res_body = call(body)

        assert res_body["type"] == INTERACTION_CALLBACK_TYPE.MODAL


@pytest.mark.parametrize(
    ("command", "custom_id"),
    [("구독추가", "add_subscription_modal"), ("슬롯동기화", "sync_slots_modal")],
)
def test_command_opens_modal(command, custom_id):
    _, body = call(interaction(TYPE.APPLICATION_COMMAND, {"name": command}))

    assert body["type"] == INTERACTION_CALLBACK_TYPE.MODAL
    assert body["data"]["custom_id"] == custom_id


def test_purchase_modal_offers_all_products():
    _, body = call(interaction(TYPE.APPLICATION_COMMAND, {"name": "구독추가"}))

    select = body["data"]["components"][2]["component"]
    assert select["custom_id"] == "product_type_select"
    assert [o["value"] for o in select["options"]] == [
        "SLOT_5",
        "SLOT_10",
        "MONTHLY_SUB_2000",
    ]


class TestSlotPurchase:
    @pytest.mark.parametrize(
        ("product", "added", "amount"),
        [("SLOT_5", 5, 3000), ("SLOT_10", 10, 5000)],
    )
    def test_adds_slots_and_records_order(self, ddb, product, added, amount):
        put_guild(ddb.table, max_limit=7, current_count=3)

        res, body = call(purchase(product))

        assert res["statusCode"] == 200
        guild = get_guild(ddb.table)
        assert guild["max_limit"] == 7 + added
        assert guild["current_count"] == 3
        [order] = get_orders(ddb.table)
        assert order["SK"].startswith("ORDER#20260131150000#")
        assert {k: v for k, v in order.items() if k not in ("PK", "SK")} == {
            "type": "ORDER",
            "guild_id": GUILD_ID,
            "buyer_discord_id": BUYER_ID,
            "product_type": product,
            "amount": amount,
            "payment_status": "SUCCESS",
            "purchased_at": FIXED_NOW.isoformat(),
            "slot_info": {
                "previous_slot": 7,
                "added_slot": added,
                "final_slot": 7 + added,
            },
        }
        assert get_item(ddb.table, f"GUILD#{GUILD_ID}", "SUB#CURRENT") is None
        assert f"기존 **7개**에서 **{7 + added}개**" in content(body)

    def test_guild_without_max_limit_starts_from_default(self, ddb):
        put_guild(ddb.table, current_count=0)

        call(purchase("SLOT_5"))

        assert get_guild(ddb.table)["max_limit"] == 10

    def test_repeated_purchases_accumulate(self, ddb):
        put_guild(ddb.table, max_limit=5)

        call(purchase("SLOT_5"))
        call(purchase("SLOT_10"))

        assert get_guild(ddb.table)["max_limit"] == 20
        assert len(get_orders(ddb.table)) == 2


def put_subscription(table, expires_at, guild_id=GUILD_ID):
    table.put_item(
        Item={
            "PK": f"GUILD#{guild_id}",
            "SK": "SUB#CURRENT",
            "type": "SUBSCRIPTION",
            "guild_id": guild_id,
            "status": "ACTIVE",
            "expires_at": expires_at,
        }
    )


class TestSlotPurchaseDuringSubscription:
    @pytest.mark.parametrize("product", ["SLOT_5", "SLOT_10"])
    def test_is_rejected_without_writes(self, ddb, product):
        put_guild(ddb.table, max_limit=250)
        put_subscription(ddb.table, "9999-12-31T00:00:00+00:00")

        _, body = call(purchase(product))

        assert content(body) == (
            f"❌ 구독 중인 서버는 슬롯을 구매할 수 없습니다. (Guild ID: {GUILD_ID})"
        )
        assert body["data"]["flags"] == 64
        assert get_guild(ddb.table)["max_limit"] == 250
        assert get_orders(ddb.table) == []

    def test_expired_subscription_allows_slot_purchase(self, ddb):
        put_guild(ddb.table, max_limit=5)
        put_subscription(ddb.table, "2000-01-01T00:00:00+00:00")

        call(purchase("SLOT_5"))

        assert get_guild(ddb.table)["max_limit"] == 10

    def test_renewal_extends_from_current_expiry(self, ddb):
        put_guild(ddb.table, max_limit=250)
        put_subscription(ddb.table, "2099-06-01T00:00:00+00:00")

        _, body = call(purchase("MONTHLY_SUB_2000"))

        assert "월 정기 구독 등록 완료" in content(body)
        assert len(get_orders(ddb.table)) == 1
        sub = get_item(ddb.table, f"GUILD#{GUILD_ID}", "SUB#CURRENT")
        assert sub["expires_at"] == "2099-07-01T00:00:00+00:00"
        assert sub["purchased_at"] == FIXED_NOW.isoformat()

    def test_expired_subscription_renews_from_now(self, ddb):
        put_guild(ddb.table, max_limit=250)
        put_subscription(ddb.table, "2000-01-01T00:00:00+00:00")

        call(purchase("MONTHLY_SUB_2000"))

        sub = get_item(ddb.table, f"GUILD#{GUILD_ID}", "SUB#CURRENT")
        assert sub["expires_at"] == "2026-02-28T15:00:00+00:00"


class TestMonthlySubscription:
    def test_creates_subscription_and_raises_limit(self, ddb):
        put_guild(ddb.table, max_limit=15, current_count=4)

        res, body = call(purchase("MONTHLY_SUB_2000"))

        assert res["statusCode"] == 200
        guild = get_guild(ddb.table)
        assert guild["max_limit"] == 250
        assert guild["current_count"] == 4

        sub = get_item(ddb.table, f"GUILD#{GUILD_ID}", "SUB#CURRENT")
        assert sub == {
            "PK": f"GUILD#{GUILD_ID}",
            "SK": "SUB#CURRENT",
            "type": "SUBSCRIPTION",
            "guild_id": GUILD_ID,
            "buyer_discord_id": BUYER_ID,
            "plan_type": "MONTHLY_SUB_2000",
            "status": "ACTIVE",
            "amount": 2000,
            "purchased_at": "2026-01-31T15:00:00+00:00",
            # 1월 31일의 한 달 뒤는 2월 말일이다.
            "expires_at": "2026-02-28T15:00:00+00:00",
            "auto_renew": False,
        }

        [order] = get_orders(ddb.table)
        assert order["product_type"] == "MONTHLY_SUB_2000"
        assert order["amount"] == 2000
        assert order["payment_status"] == "SUCCESS"
        assert order["slot_info"] == {"previous_slot": 15, "final_slot": 250}

        # 만료일은 KST로 보여준다. (UTC 15시 = 다음 날 KST 0시)
        assert "구독 만료일: `2026-03-01 00:00:00 KST`" in content(body)

    def test_activates_guild_notifications_only(self, ddb):
        put_guild(ddb.table, max_limit=5)
        put_guild(ddb.table, guild_id="2", max_limit=5)
        put_noti(ddb.table, "10")
        put_noti(ddb.table, "11")
        put_noti(ddb.table, "20", guild_id="2")

        call(purchase("MONTHLY_SUB_2000"))

        for channel_id in ("10", "11"):
            noti = get_item(ddb.table, "CHZZK#abc", f"NOTI#{channel_id}")
            assert noti["is_subscription_active"] is True
        other = get_item(ddb.table, "CHZZK#abc", "NOTI#20")
        assert "is_subscription_active" not in other
        # GUILD/SUB/ORDER 아이템에는 플래그를 쓰지 않는다.
        assert "is_subscription_active" not in get_guild(ddb.table)


class TestPurchaseErrors:
    def test_unknown_product_is_rejected_without_writes(self, ddb):
        put_guild(ddb.table, max_limit=5)

        _, body = call(purchase("SLOT_99"))

        assert content(body) == "❌ 알 수 없는 상품입니다: `SLOT_99`"
        assert body["data"]["flags"] == 64
        assert get_guild(ddb.table)["max_limit"] == 5
        assert get_orders(ddb.table) == []

    def test_unknown_guild_is_rejected_without_writes(self, ddb):
        _, body = call(purchase("MONTHLY_SUB_2000"))

        assert "해당 길드 정보를 찾을 수 없습니다" in content(body)
        assert body["data"]["flags"] == 64
        assert get_orders(ddb.table) == []
        assert get_item(ddb.table, f"GUILD#{GUILD_ID}", "SUB#CURRENT") is None

    def test_dynamodb_error_is_reported_and_nothing_changes(self, mocker, ddb):
        put_guild(ddb.table, max_limit=5)
        mocker.patch.object(
            ddb.client,
            "transact_write_items",
            side_effect=ClientError(
                {"Error": {"Code": "InternalServerError", "Message": "boom"}},
                "TransactWriteItems",
            ),
        )

        res, body = call(purchase("SLOT_5"))

        assert res["statusCode"] == 200
        assert content(body).startswith("❌ 처리 중 오류가 발생했습니다")
        assert get_guild(ddb.table)["max_limit"] == 5


class TestSyncSlots:
    def test_fixes_out_of_sync_count(self, ddb):
        put_guild(ddb.table, max_limit=10, current_count=5)
        put_noti(ddb.table, "10")
        put_noti(ddb.table, "11")
        put_noti(ddb.table, "20", guild_id="2")

        _, body = call(sync_slots())

        assert get_guild(ddb.table)["current_count"] == 2
        assert "정합성 보정 완료" in content(body)
        assert "**2개** (기존 DB 기록: 5개)" in content(body)

    def test_in_sync_count_is_left_alone(self, mocker, ddb):
        put_guild(ddb.table, max_limit=10, current_count=1)
        put_noti(ddb.table, "10")
        update_item = mocker.spy(ddb.client, "update_item")

        _, body = call(sync_slots())

        assert "정합성 확인 완료" in content(body)
        assert update_item.call_count == 0
        assert get_guild(ddb.table)["current_count"] == 1

    def test_guild_without_items_is_reported(self):
        _, body = call(sync_slots(guild_id="404"))

        assert "해당 서버 정보를 찾을 수 없습니다" in content(body)

    def test_notifications_without_guild_item_are_reported(self, ddb):
        put_noti(ddb.table, "10")

        _, body = call(sync_slots())

        assert f"`GUILD#{GUILD_ID}`" in content(body)
        assert get_guild(ddb.table) is None


def test_unknown_interaction_is_answered():
    _, body = call(interaction(TYPE.MODAL_SUBMIT, {"custom_id": "unknown"}))

    assert content(body) == "알 수 없는 요청입니다."


def test_sync_slots_dynamodb_error_is_reported(mocker, ddb):
    mocker.patch.object(
        ddb.client,
        "query",
        side_effect=ClientError(
            {"Error": {"Code": "InternalServerError", "Message": "boom"}}, "Query"
        ),
    )

    _, body = call(sync_slots())

    assert content(body).startswith("❌ 슬롯 동기화 중 오류가 발생했습니다")
    assert body["data"]["flags"] == 64
