import json
import logging
import os
import uuid
from datetime import UTC, datetime

from bot.admin_discord_interactions import service
from bot.admin_discord_interactions.purchase import (
    DEFAULT_MAX_LIMIT,
    MONTHLY_SUB,
    SLOT_PRODUCTS,
    build_purchase,
    order_sk,
)
from bot.admin_discord_interactions.sync_slots import fixed_message, in_sync_message
from bot.admin_discord_interactions.ui import (
    ADD_SUBSCRIPTION_MODAL,
    SYNC_SLOTS_MODAL,
    parse_modal_values,
)
from shared import TYPE, middleware
from shared.discord.bot import (
    INVALID_SIGNATURE_RESPONSE,
    PONG,
    reply,
    verify_signature,
)
from shared.notification_dispatcher import (
    activate_subscription_for_guild,
    is_guild_subscription_active,
    query_guild_items,
)
from shared.slots import count_slot_usage
from shared.utils import build_response

ADMIN_DISCORD_PUBLIC_KEY = os.environ.get("ADMIN_DISCORD_PUBLIC_KEY")
ADMIN_DISCORD_USER_ID = os.environ.get("ADMIN_DISCORD_USER_ID")

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
def handler(event, _context):
    raw_body = event["body"]
    if not verify_signature(ADMIN_DISCORD_PUBLIC_KEY, event["headers"], raw_body):
        return INVALID_SIGNATURE_RESPONSE

    body = json.loads(raw_body)
    logger.info(
        json.dumps({"type": "ADMIN_REQUEST_BODY", "body": raw_body}, ensure_ascii=False)
    )

    if body.get("type") == TYPE.PING:
        return build_response(200, data=PONG)

    user = body.get("member", {}).get("user", {}) or body.get("user", {})
    user_id = user.get("id")
    if user_id != ADMIN_DISCORD_USER_ID:
        logger.info(
            json.dumps(
                {"type": "UNAUTHORIZED_ADMIN_ACCESS", "user_id": user_id},
                ensure_ascii=False,
            )
        )
        return build_response(
            200,
            data=reply("❌ 이 봇을 사용할 수 있는 권한이 없습니다.", ephemeral=True),
        )

    return build_response(200, data=_dispatch(body))


def _dispatch(body: dict) -> dict:
    interaction_type = body.get("type")
    data = body.get("data", {})
    logger.info(
        json.dumps(
            {"type": "ADMIN_INTERACTION_TYPE", "interaction_type": interaction_type},
            ensure_ascii=False,
        )
    )

    if interaction_type == TYPE.APPLICATION_COMMAND:
        command_name = data.get("name")
        logger.info(
            json.dumps(
                {"type": "ADMIN_COMMAND_NAME", "command_name": command_name},
                ensure_ascii=False,
            )
        )
        modal = COMMAND_MODALS.get(command_name)
        if modal is not None:
            return modal

    if interaction_type == TYPE.MODAL_SUBMIT:
        submit = MODAL_SUBMIT_HANDLERS.get(data.get("custom_id"))
        if submit is not None:
            return submit(parse_modal_values(data.get("components", [])))

    return reply("알 수 없는 요청입니다.", ephemeral=True)


def add_subscription(values: dict[str, str]) -> dict:
    guild_id = values.get("guild_id_input")
    buyer_id = values.get("buyer_id_input")
    product_type = values.get("product_type_select")

    try:
        # GUILD 아이템은 알림을 처음 등록할 때 생기므로, 없으면 처리하지 않는다.
        guild = service.get_guild(guild_id)
        if guild is None:
            return reply(
                f"❌ 해당 길드 정보를 찾을 수 없습니다. (Guild ID: {guild_id})",
                ephemeral=True,
            )

        if product_type in SLOT_PRODUCTS and is_guild_subscription_active(guild_id):
            return reply(
                f"❌ 구독 중인 서버는 슬롯을 구매할 수 없습니다. (Guild ID: {guild_id})",
                ephemeral=True,
            )

        now = datetime.now(UTC)
        purchase = build_purchase(
            guild_id=guild_id,
            buyer_id=buyer_id,
            product_type=product_type,
            old_max_limit=int(guild.get("max_limit", DEFAULT_MAX_LIMIT)),
            now=now,
            sk=order_sk(now, str(uuid.uuid4())[:16]),
            current_subscription=(
                service.get_subscription(guild_id)
                if product_type == MONTHLY_SUB
                else None
            ),
        )
        if purchase is None:
            return reply(f"❌ 알 수 없는 상품입니다: `{product_type}`", ephemeral=True)

        service.save_purchase(guild_id, purchase)
        if purchase.subscription_item is not None:
            activate_subscription_for_guild(guild_id)
        return reply(purchase.message)

    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "UPDATE_SUBSCRIPTION_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        return reply(f"❌ 처리 중 오류가 발생했습니다: {e}")


def sync_slots(values: dict[str, str]) -> dict:
    guild_id = str(values.get("guild_id_input"))

    try:
        items = query_guild_items(guild_id)
        if not items:
            return reply(
                f"❌ 해당 서버 정보를 찾을 수 없습니다. (Guild ID: `{guild_id}`)"
            )

        usage = count_slot_usage(guild_id, items)
        if usage is None:
            return reply(f"❌ 서버 메타데이터(`GUILD#{guild_id}`)를 찾을 수 없습니다.")

        logger.info(
            json.dumps(
                {
                    "type": "SYNC_SLOTS_INFO",
                    "guild_id": guild_id,
                    "noti_count": usage.noti_count,
                    "old_current_count": usage.current_count,
                    "max_limit": usage.max_limit,
                },
                ensure_ascii=False,
            )
        )
        if usage.in_sync:
            return reply(in_sync_message(guild_id, usage))

        service.set_current_count(guild_id, usage.noti_count)
        return reply(fixed_message(guild_id, usage))

    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "SYNC_SLOTS_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        return reply(f"❌ 슬롯 동기화 중 오류가 발생했습니다: {e}", ephemeral=True)


COMMAND_MODALS = {
    "구독추가": ADD_SUBSCRIPTION_MODAL,
    "슬롯동기화": SYNC_SLOTS_MODAL,
}

MODAL_SUBMIT_HANDLERS = {
    "add_subscription_modal": add_subscription,
    "sync_slots_modal": sync_slots,
}
