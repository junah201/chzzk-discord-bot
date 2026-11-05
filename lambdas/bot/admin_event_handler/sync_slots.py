from dataclasses import dataclass


@dataclass(frozen=True)
class SlotUsage:
    noti_count: int
    current_count: int
    max_limit: int

    @property
    def in_sync(self) -> bool:
        return self.noti_count == self.current_count


def count_slot_usage(guild_id: str, items: list[dict]) -> SlotUsage | None:
    """GSI로 조회한 길드 아이템에서 실제 NOTI 수와 GUILD 아이템의 기록값을 꺼냅니다.
    GUILD 아이템이 없으면 None을 반환합니다.
    """
    guild_pk = f"GUILD#{guild_id}"
    noti_count = 0
    guild_item = None
    for item in items:
        item_type = item.get("type", {}).get("S", "")
        if item_type == "NOTI":
            noti_count += 1
        elif item_type == "GUILD" or item.get("SK", {}).get("S", "") == guild_pk:
            guild_item = item

    if guild_item is None:
        return None
    return SlotUsage(
        noti_count=noti_count,
        current_count=int(guild_item.get("current_count", {}).get("N", "0")),
        max_limit=int(guild_item.get("max_limit", {}).get("N", "5")),
    )


def in_sync_message(guild_id: str, usage: SlotUsage) -> str:
    return (
        f"**슬롯 데이터 정합성 확인 완료!**\n"
        f"- **길드 ID**: `{guild_id}`\n"
        f"- 실제 등록된 알림 수: **{usage.noti_count}개**\n"
        f"- DB 기록된 사용 중인 알림 수: **{usage.current_count}개**\n"
        f"- 최대 이용 가능 슬롯: **{usage.max_limit}개**"
    )


def fixed_message(guild_id: str, usage: SlotUsage) -> str:
    return (
        f"**슬롯 데이터 정합성 보정 완료!**\n"
        f"- **길드 ID**: `{guild_id}`\n"
        f"- **실제 등록된 알림 수**: **{usage.noti_count}개** (기존 DB 기록: {usage.current_count}개)\n"
        f"- **최대 이용 가능 슬롯**: **{usage.max_limit}개**"
    )
