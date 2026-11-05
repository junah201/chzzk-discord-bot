from datetime import UTC, datetime

import pytest
from bot.admin_event_handler.purchase import build_purchase, order_sk, renewal_base

NOW = datetime(2026, 1, 31, 15, 0, 0, tzinfo=UTC)
SK = "ORDER#20260131150000#abc"


def purchase(product_type, old_max_limit=7, current_subscription=None):
    return build_purchase(
        guild_id="1",
        buyer_id="42",
        product_type=product_type,
        old_max_limit=old_max_limit,
        now=NOW,
        sk=SK,
        current_subscription=current_subscription,
    )


def test_order_sk():
    assert order_sk(NOW, "abc") == SK


@pytest.mark.parametrize(
    ("product", "added", "amount"),
    [("SLOT_5", 5, 3000), ("SLOT_10", 10, 5000)],
)
def test_slot_purchase(product, added, amount):
    result = purchase(product)

    assert result.new_max_limit == 7 + added
    assert result.subscription_item is None
    assert result.order_item == {
        "PK": {"S": "GUILD#1"},
        "SK": {"S": SK},
        "type": {"S": "ORDER"},
        "guild_id": {"S": "1"},
        "buyer_discord_id": {"S": "42"},
        "product_type": {"S": product},
        "amount": {"N": str(amount)},
        "payment_status": {"S": "SUCCESS"},
        "purchased_at": {"S": "2026-01-31T15:00:00+00:00"},
        "slot_info": {
            "M": {
                "previous_slot": {"N": "7"},
                "added_slot": {"N": str(added)},
                "final_slot": {"N": str(7 + added)},
            }
        },
    }
    assert f"`₩{amount:,} 단일 구매 (+{added}개)`" in result.message
    assert f"기존 **7개**에서 **{7 + added}개**" in result.message


def test_monthly_subscription():
    result = purchase("MONTHLY_SUB_2000", old_max_limit=15)

    assert result.new_max_limit == 250
    assert result.order_item["amount"] == {"N": "2000"}
    assert result.order_item["slot_info"] == {
        "M": {"previous_slot": {"N": "15"}, "final_slot": {"N": "250"}}
    }
    sub = result.subscription_item
    assert sub["SK"] == {"S": "SUB#CURRENT"}
    assert sub["status"] == {"S": "ACTIVE"}
    # 1월 31일의 한 달 뒤는 2월 말일이다.
    assert sub["expires_at"] == {"S": "2026-02-28T15:00:00+00:00"}
    assert "구독 만료일: `2026-03-01 00:00:00 KST`" in result.message


def test_unknown_product_returns_none():
    assert purchase("SLOT_99") is None


def subscription(status="ACTIVE", expires_at="2026-03-10T00:00:00+00:00"):
    return {"status": status, "expires_at": expires_at}


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        (None, NOW),
        (subscription(), datetime(2026, 3, 10, tzinfo=UTC)),
        (subscription(expires_at="2026-01-01T00:00:00+00:00"), NOW),
        (subscription(status="EXPIRED"), NOW),
        (subscription(status="SUSPENDED"), NOW),
        ({"status": "ACTIVE"}, NOW),
    ],
    ids=["none", "active", "already-expired", "expired", "suspended", "no-expiry"],
)
def test_renewal_base(current, expected):
    assert renewal_base(NOW, current) == expected


def test_renewal_extends_from_current_expiry():
    result = purchase("MONTHLY_SUB_2000", current_subscription=subscription())

    sub = result.subscription_item
    assert sub["expires_at"] == {"S": "2026-04-10T00:00:00+00:00"}
    assert sub["purchased_at"] == {"S": "2026-01-31T15:00:00+00:00"}
    assert "구독 만료일: `2026-04-10 09:00:00 KST`" in result.message
