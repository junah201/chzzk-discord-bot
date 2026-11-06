from shared.slots import SlotUsage


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
