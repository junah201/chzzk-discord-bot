from shared import COMPONENT_TYPE, INTERACTION_CALLBACK_TYPE, TEXT_INPUT_STYLE


def _text_input(label: str, custom_id: str, placeholder: str) -> dict:
    return {
        "type": COMPONENT_TYPE.LABEL,
        "label": label,
        "component": {
            "type": COMPONENT_TYPE.TEXT_INPUT,
            "custom_id": custom_id,
            "style": TEXT_INPUT_STYLE.SHORT,
            "placeholder": placeholder,
            "required": True,
        },
    }


def _modal(custom_id: str, title: str, components: list[dict]) -> dict:
    return {
        "type": INTERACTION_CALLBACK_TYPE.MODAL,
        "data": {"custom_id": custom_id, "title": title, "components": components},
    }


ADD_SUBSCRIPTION_MODAL = _modal(
    "add_subscription_modal",
    "수동 결제 / 구독 추가",
    [
        _text_input("대상 길드 ID 입력", "guild_id_input", "1192328115419099207"),
        _text_input("구매자 디스코드 ID 입력", "buyer_id_input", "유저 ID 입력"),
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
)

SYNC_SLOTS_MODAL = _modal(
    "sync_slots_modal",
    "슬롯 데이터 정합성 동기화",
    [
        _text_input(
            "동기화할 대상 서버 ID 입력", "guild_id_input", "1192328115419099207"
        ),
    ],
)


def parse_modal_values(components: list[dict]) -> dict[str, str]:
    """모달 제출값을 custom_id별로 모읍니다. Text Input은 value, Select는 values[0]을 씁니다."""
    values = {}
    for row in components:
        item = row.get("component", {})
        if "value" in item:
            values[item.get("custom_id")] = item.get("value")
        elif "values" in item:
            values[item.get("custom_id")] = item.get("values", [])[0]
    return values
