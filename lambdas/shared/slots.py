from dataclasses import dataclass


@dataclass(frozen=True)
class SlotUsage:
    noti_count: int
    current_count: int
    max_limit: int

    @property
    def in_sync(self) -> bool:
        return self.noti_count == self.current_count


def count_notifications(items: list[dict]) -> int:
    return sum(1 for item in items if item.get("type", {}).get("S", "") == "NOTI")


def count_slot_usage(guild_id: str, items: list[dict]) -> SlotUsage | None:
    """GSI로 조회한 길드 아이템에서 실제 NOTI 수와 GUILD 아이템의 기록값을 꺼냅니다.
    GUILD 아이템이 없으면 None을 반환합니다.
    """
    guild_pk = f"GUILD#{guild_id}"
    guild_item = next(
        (
            item
            for item in items
            if item.get("type", {}).get("S", "") == "GUILD"
            or item.get("SK", {}).get("S", "") == guild_pk
        ),
        None,
    )

    if guild_item is None:
        return None
    return SlotUsage(
        noti_count=count_notifications(items),
        current_count=int(guild_item.get("current_count", {}).get("N", "0")),
        max_limit=int(guild_item.get("max_limit", {}).get("N", "5")),
    )
