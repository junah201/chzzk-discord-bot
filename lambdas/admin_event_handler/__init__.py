import json
import logging
import os
import uuid
from datetime import datetime
from typing import Literal

import boto3
from dateutil.relativedelta import relativedelta
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from shared import INTERACTION_CALLBACK_TYPE, TYPE, middleware
from shared.discord.dataclass import COMPONENT_TYPE, TEXT_INPUT_STYLE
from shared.utils import build_response

ADMIN_DISCORD_PUBLIC_KEY = os.environ.get("ADMIN_DISCORD_PUBLIC_KEY")
ADMIN_DISCORD_USER_ID = os.environ.get("ADMIN_DISCORD_USER_ID")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_resource = boto3.resource("dynamodb")
dynamodb_client = boto3.client("dynamodb")
table_name = "chzzk-bot-db"
table = dynamodb_resource.Table(table_name)


@middleware(logger)
def handler(event, context):
    # 서명 검증
    try:
        raw_body = event["body"]
        signature = event["headers"].get("x-signature-ed25519")
        timestamp = event["headers"].get("x-signature-timestamp")

        verify_key = VerifyKey(bytes.fromhex(ADMIN_DISCORD_PUBLIC_KEY))
        verify_key.verify(f"{timestamp}{raw_body}".encode(), bytes.fromhex(signature))
    except BadSignatureError as e:
        logger.info(
            json.dumps(
                {"type": "INVALID_REQUEST_SIGNATURE", "exception": str(e)},
                ensure_ascii=False,
            )
        )
        return {"statusCode": 401, "body": "Invalid request signature"}

    body = json.loads(raw_body)
    logger.info(
        json.dumps({"type": "ADMIN_REQUEST_BODY", "body": raw_body}, ensure_ascii=False)
    )

    if body.get("type") == TYPE.PING:
        return build_response(200, data={"type": 1})

    # 관리자 권한 확인
    user_data = body.get("member", {}).get("user", {}) or body.get("user", {})
    user_id = user_data.get("id")

    if user_id != ADMIN_DISCORD_USER_ID:
        logger.info(
            json.dumps(
                {"type": "UNAUTHORIZED_ADMIN_ACCESS", "user_id": user_id},
                ensure_ascii=False,
            )
        )
        return build_response(
            200,
            data={
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": "❌ 이 봇을 사용할 수 있는 권한이 없습니다.",
                    "flags": 64,
                },
            },
        )

    interaction_type = body.get("type")

    logger.info(
        json.dumps(
            {"type": "ADMIN_INTERACTION_TYPE", "interaction_type": interaction_type},
            ensure_ascii=False,
        )
    )

    # 구독 추가
    if interaction_type == TYPE.APPLICATION_COMMAND:
        command_name = body.get("data", {}).get("name")

        logger.info(
            json.dumps(
                {"type": "ADMIN_COMMAND_NAME", "command_name": command_name},
                ensure_ascii=False,
            )
        )

        if command_name == "구독추가":
            return build_response(
                200,
                data={
                    "type": INTERACTION_CALLBACK_TYPE.MODAL,
                    "data": {
                        "custom_id": "add_subscription_modal",
                        "title": "수동 결제 / 구독 추가",
                        "components": [
                            {
                                "type": COMPONENT_TYPE.LABEL,
                                "label": "대상 길드 ID 입력",
                                "component": {
                                    "type": COMPONENT_TYPE.TEXT_INPUT,
                                    "custom_id": "guild_id_input",
                                    "style": TEXT_INPUT_STYLE.SHORT,
                                    "placeholder": "1553352969628549180",
                                    "required": True,
                                },
                            },
                            {
                                "type": COMPONENT_TYPE.LABEL,
                                "label": "구매자 디스코드 ID 입력",
                                "component": {
                                    "type": COMPONENT_TYPE.TEXT_INPUT,
                                    "custom_id": "buyer_id_input",
                                    "style": TEXT_INPUT_STYLE.SHORT,
                                    "placeholder": "유저 ID 입력",
                                    "required": True,
                                },
                            },
                            {
                                "type": COMPONENT_TYPE.LABEL,
                                "label": "상품 선택",
                                "component": {
                                    "type": COMPONENT_TYPE.STRING_SELECT,
                                    "custom_id": "product_type_select",
                                    "placeholder": "상품을 선택하세요",
                                    "min_values": 1,
                                    "max_values": 1,
                                    "options": [
                                        {
                                            "label": "₩3,000 단일 구매 (슬롯 5개 추가)",
                                            "value": "SLOT_5",
                                            "description": "서버 슬롯 5개가 영구 추가됩니다.",
                                        },
                                        {
                                            "label": "₩5,000 단일 구매 (슬롯 10개 추가)",
                                            "value": "SLOT_10",
                                            "description": "서버 슬롯 10개가 영구 추가됩니다.",
                                        },
                                        {
                                            "label": "월 ₩2,000 정기 구독",
                                            "value": "MONTHLY_SUB_2000",
                                            "description": "한 달 동안 구독이 유지됩니다.",
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                },
            )

    if interaction_type == TYPE.MODAL_SUBMIT:
        custom_id = body.get("data", {}).get("custom_id")

        if custom_id == "add_subscription_modal":
            # 입력값 및 선택값 파싱
            components = body.get("data", {}).get("components", [])
            form_values = {}
            for row in components:
                item = row.get("component", {})
                # Text Input은 'value', Select Menu는 'values' 배열로 값이 들어옴
                if "value" in item:
                    form_values[item.get("custom_id")] = item.get("value")
                elif "values" in item:
                    form_values[item.get("custom_id")] = item.get("values", [])[0]

            guild_id = form_values.get("guild_id_input")
            buyer_id = form_values.get("buyer_id_input")
            product_type: Literal["SLOT_5", "SLOT_10", "MONTHLY_SUB_2000"] = form_values.get("product_type_select")

            try:
                guild_pk = f"GUILD#{guild_id}"

                # 트랜잭션 또는 개별 조회를 통한 길드 존재 여부 확인
                response = table.get_item(Key={"PK": guild_pk, "SK": guild_pk})
                if "Item" not in response:
                    return build_response(
                        200,
                        data={
                            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                            "data": {
                                "content": f"❌ 해당 길드 정보를 찾을 수 없습니다. (Guild ID: {guild_id})",
                                "flags": 64,
                            },
                        },
                    )

                item = response["Item"]
                result_message = ""

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                short_uuid = str(uuid.uuid4())[:16]
                order_sk = f"ORDER#{timestamp}#{short_uuid}"
                now = datetime.now()
                purchased_at_str = now.isoformat()
                old_max_limit = int(item.get("max_limit", 5))

                # 상품 종류별 처리
                if product_type in ["SLOT_5", "SLOT_10"]:
                    added_slots = 5 if product_type == "SLOT_5" else 10
                    amount = 3000 if product_type == "SLOT_5" else 5000
                    new_max_limit = old_max_limit + added_slots

                    order_item = {
                        "PK": {"S": guild_pk},
                        "SK": {"S": order_sk},
                        "type": {"S": "ORDER"},
                        "guild_id": {"S": guild_id},
                        "buyer_discord_id": {"S": buyer_id},
                        "product_type": {"S": product_type},
                        "amount": {"N": str(amount)},
                        "payment_status": {"S": "SUCCESS"},
                        "purchased_at": {"S": purchased_at_str},
                        "slot_info": {
                            "M": {
                                "previous_slot": {"N": str(old_max_limit)},
                                "added_slot": {"N": str(added_slots)},
                                "final_slot": {"N": str(new_max_limit)},
                            }
                        },
                    }

                    dynamodb_client.transact_write_items(
                        TransactItems=[
                            {
                                "Put": {
                                    "TableName": table_name,
                                    "Item": order_item,
                                    "ConditionExpression": "attribute_not_exists(SK)",
                                }
                            },
                            {
                                "Update": {
                                    "TableName": table_name,
                                    "Key": {
                                        "PK": {"S": guild_pk},
                                        "SK": {"S": guild_pk},
                                    },
                                    "UpdateExpression": "SET max_limit = :new_limit",
                                    "ExpressionAttributeValues": {
                                        ":new_limit": {"N": str(new_max_limit)}
                                    },
                                }
                            },
                        ]
                    )

                    result_message = (
                        f"**단일 구매 슬롯 추가 완료!**\n"
                        f"- 서버 ID: `{guild_id}`\n"
                        f"- 구매자 ID: `{buyer_id}`\n"
                        f"- 상품: `₩{3000 if added_slots == 5 else 5000:,} 단일 구매 (+{added_slots}개)`\n"
                        f"- 슬롯 변경: 기존 **{old_max_limit}개**에서 **{new_max_limit}개**로 늘어났습니다."
                    )

                elif product_type == "MONTHLY_SUB_2000":

                    # 정확히 1달 뒤로 계산 (예: 1월 20일 -> 2월 20일)
                    expires_at = now + relativedelta(months=1)

                    expires_at_str = expires_at.isoformat()

                    timestamp_str = now.strftime("%Y%m%d%H%M%S")
                    short_uuid = str(uuid.uuid4())[:8]
                    order_sk = f"ORDER#{timestamp_str}#{short_uuid}"

                    new_max_limit = 250

                    order_item = {
                        "PK": {"S": guild_pk},
                        "SK": {"S": order_sk},
                        "type": {"S": "ORDER"},
                        "guild_id": {"S": guild_id},
                        "buyer_discord_id": {"S": buyer_id},
                        "product_type": {"S": "MONTHLY_SUB_2000"},
                        "amount": {"N": "2000"},
                        "payment_status": {"S": "SUCCESS"},
                        "purchased_at": {"S": purchased_at_str},
                        "slot_info": {
                            "M": {
                                "previous_slot": {"N": str(old_max_limit)},
                                "final_slot": {"N": str(new_max_limit)},
                            }
                        },
                    }

                    sub_item = {
                        "PK": {"S": guild_pk},
                        "SK": {"S": "SUB#CURRENT"},
                        "type": {"S": "SUBSCRIPTION"},
                        "guild_id": {"S": guild_id},
                        "buyer_discord_id": {"S": buyer_id},
                        "plan_type": {"S": "MONTHLY_SUB_2000"},
                        "status": {"S": "ACTIVE"},
                        "amount": {"N": "2000"},
                        "purchased_at": {"S": purchased_at_str},
                        "expires_at": {"S": expires_at_str},
                        "auto_renew": {"BOOL": False},
                    }

                    dynamodb_client.transact_write_items(
                        TransactItems=[
                            {
                                "Put": {
                                    "TableName": table_name,
                                    "Item": order_item,
                                }
                            },
                            {
                                "Put": {
                                    "TableName": table_name,
                                    "Item": sub_item,
                                }
                            },
                            {
                                "Update": {
                                    "TableName": table_name,
                                    "Key": {
                                        "PK": {"S": guild_pk},
                                        "SK": {"S": guild_pk},
                                    },
                                    "UpdateExpression": "SET max_limit = :max_limit",
                                    "ExpressionAttributeValues": {
                                        ":max_limit": {"N": str(new_max_limit)}
                                    },
                                }
                            },
                        ]
                    )

                    result_message = (
                        f"**월 정기 구독 등록 완료!**\n"
                        f"- 서버 ID: `{guild_id}`\n"
                        f"- 구매자 ID: `{buyer_id}`\n"
                        f"- 상품: `월 ₩2,000 정기 구독`\n"
                        f"- 슬롯 변경: 기존 **{old_max_limit}개**에서 **{new_max_limit}개**로 늘어났습니다.\n"
                        f"- 구독 만료일: `{expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC`"
                    )

                return build_response(
                    200,
                    data={
                        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {
                            "content": result_message,
                        },
                    },
                )

            except Exception as e:
                logger.error(
                    json.dumps(
                        {"type": "UPDATE_SUBSCRIPTION_ERROR", "error": str(e)},
                        ensure_ascii=False,
                    )
                )
                return build_response(
                    200,
                    data={
                        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                        "data": {
                            "content": f"❌ 처리 중 오류가 발생했습니다: {str(e)}",
                        },
                    },
                )

    return build_response(
        200,
        data={
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {"content": "알 수 없는 요청입니다.", "flags": 64},
        },
    )
