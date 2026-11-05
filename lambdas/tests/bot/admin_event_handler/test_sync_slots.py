from bot.admin_event_handler.sync_slots import SlotUsage, count_slot_usage


def guild(**attrs):
    return {
        "PK": {"S": "GUILD#1"},
        "SK": {"S": "GUILD#1"},
        "type": {"S": "GUILD"},
        **{k: {"N": str(v)} for k, v in attrs.items()},
    }


def noti():
    return {"type": {"S": "NOTI"}}


def test_counts_notifications():
    usage = count_slot_usage(
        "1", [noti(), guild(current_count=3, max_limit=10), noti()]
    )

    assert usage == SlotUsage(noti_count=2, current_count=3, max_limit=10)
    assert usage.in_sync is False


def test_missing_counts_use_defaults():
    assert count_slot_usage("1", [guild()]) == SlotUsage(0, 0, 5)


def test_in_sync():
    assert count_slot_usage("1", [noti(), guild(current_count=1)]).in_sync is True


def test_guild_item_found_by_sk_without_type():
    item = guild(current_count=2)
    del item["type"]

    assert count_slot_usage("1", [item]).current_count == 2


def test_without_guild_item_returns_none():
    assert count_slot_usage("1", [noti()]) is None
