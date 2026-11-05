from dataclasses import dataclass
from datetime import datetime

from dateutil.relativedelta import relativedelta
from shared.utils import to_kst_string

# 상품 코드: (추가 슬롯 수, 가격)
SLOT_PRODUCTS = {"SLOT_5": (5, 3000), "SLOT_10": (10, 5000)}
MONTHLY_SUB = "MONTHLY_SUB_2000"
MONTHLY_SUB_AMOUNT = 2000
SUBSCRIPTION_MAX_LIMIT = 250
DEFAULT_MAX_LIMIT = 5


@dataclass(frozen=True)
class Purchase:
    order_item: dict
    new_max_limit: int
    message: str
    subscription_item: dict | None = None


def order_sk(now: datetime, short_id: str) -> str:
    return f"ORDER#{now:%Y%m%d%H%M%S}#{short_id}"


def build_purchase(
    *,
    guild_id: str,
    buyer_id: str,
    product_type: str,
    old_max_limit: int,
    now: datetime,
    sk: str,
) -> Purchase | None:
    """상품 구매로 저장할 아이템과 결과 메시지를 만듭니다. 모르는 상품이면 None을 반환합니다."""
    if product_type in SLOT_PRODUCTS:
        return _build_slot_purchase(
            guild_id, buyer_id, product_type, old_max_limit, now, sk
        )
    if product_type == MONTHLY_SUB:
        return _build_monthly_subscription(guild_id, buyer_id, old_max_limit, now, sk)
    return None


def _order_item(
    guild_id, buyer_id, product_type, amount, now, sk, slot_info: dict
) -> dict:
    return {
        "PK": {"S": f"GUILD#{guild_id}"},
        "SK": {"S": sk},
        "type": {"S": "ORDER"},
        "guild_id": {"S": guild_id},
        "buyer_discord_id": {"S": buyer_id},
        "product_type": {"S": product_type},
        "amount": {"N": str(amount)},
        "payment_status": {"S": "SUCCESS"},
        "purchased_at": {"S": now.isoformat()},
        "slot_info": {"M": {k: {"N": str(v)} for k, v in slot_info.items()}},
    }


def _build_slot_purchase(guild_id, buyer_id, product_type, old_max_limit, now, sk):
    added_slots, amount = SLOT_PRODUCTS[product_type]
    new_max_limit = old_max_limit + added_slots
    order_item = _order_item(
        guild_id,
        buyer_id,
        product_type,
        amount,
        now,
        sk,
        {
            "previous_slot": old_max_limit,
            "added_slot": added_slots,
            "final_slot": new_max_limit,
        },
    )
    message = (
        f"**단일 구매 슬롯 추가 완료!**\n"
        f"- 서버 ID: `{guild_id}`\n"
        f"- 구매자 ID: `{buyer_id}`\n"
        f"- 상품: `₩{amount:,} 단일 구매 (+{added_slots}개)`\n"
        f"- 슬롯 변경: 기존 **{old_max_limit}개**에서 **{new_max_limit}개**로 늘어났습니다."
    )
    return Purchase(order_item=order_item, new_max_limit=new_max_limit, message=message)


def _build_monthly_subscription(guild_id, buyer_id, old_max_limit, now, sk):
    # 정확히 1달 뒤로 계산 (예: 1월 31일 -> 2월 28일)
    expires_at = now + relativedelta(months=1)
    order_item = _order_item(
        guild_id,
        buyer_id,
        MONTHLY_SUB,
        MONTHLY_SUB_AMOUNT,
        now,
        sk,
        {"previous_slot": old_max_limit, "final_slot": SUBSCRIPTION_MAX_LIMIT},
    )
    subscription_item = {
        "PK": {"S": f"GUILD#{guild_id}"},
        "SK": {"S": "SUB#CURRENT"},
        "type": {"S": "SUBSCRIPTION"},
        "guild_id": {"S": guild_id},
        "buyer_discord_id": {"S": buyer_id},
        "plan_type": {"S": MONTHLY_SUB},
        "status": {"S": "ACTIVE"},
        "amount": {"N": str(MONTHLY_SUB_AMOUNT)},
        "purchased_at": {"S": now.isoformat()},
        "expires_at": {"S": expires_at.isoformat()},
        "auto_renew": {"BOOL": False},
    }
    message = (
        f"**월 정기 구독 등록 완료!**\n"
        f"- 서버 ID: `{guild_id}`\n"
        f"- 구매자 ID: `{buyer_id}`\n"
        f"- 상품: `월 ₩{MONTHLY_SUB_AMOUNT:,} 정기 구독`\n"
        f"- 슬롯 변경: 기존 **{old_max_limit}개**에서 **{SUBSCRIPTION_MAX_LIMIT}개**로 늘어났습니다.\n"
        f"- 구독 만료일: `{to_kst_string(expires_at)} KST`"
    )
    return Purchase(
        order_item=order_item,
        new_max_limit=SUBSCRIPTION_MAX_LIMIT,
        message=message,
        subscription_item=subscription_item,
    )
