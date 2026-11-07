from datetime import UTC, datetime

import pytest
from cron.live_check.logic import (
    ChannelResult,
    LiveCheckStats,
    delivery_update,
    is_new_live,
    live_from_following,
    parse_account_index,
    should_notify,
)

NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
CHZZK = {
    "liveId": 200,
    "channel": {"channelName": "스트리머", "channelImageUrl": "https://img"},
}


def test_parse_account_index():
    assert parse_account_index({"index": 3}) == 3


def test_live_from_following_merges_channel_into_live_info():
    channel = {"channelId": "a", "channelName": "n", "channelImageUrl": "i"}
    following = {
        "channel": channel,
        "streamer": {"openLive": True},
        "liveInfo": {"liveId": 1, "liveTitle": "t"},
    }

    assert live_from_following(following) == {
        "liveId": 1,
        "liveTitle": "t",
        "channel": channel,
    }


@pytest.mark.parametrize(("adult", "expected"), [(True, None), (False, "thumb")])
def test_live_from_following_hides_adult_thumbnail(adult, expected):
    following = {
        "channel": {"channelId": "a"},
        "liveInfo": {"liveId": 1, "liveImageUrl": "thumb", "adult": adult},
    }

    assert live_from_following(following)["liveImageUrl"] == expected


@pytest.mark.parametrize("live_info", [None, {}, {"liveTitle": "t"}])
def test_live_from_following_without_live_id(live_info):
    following = {"channel": {"channelId": "a"}, "liveInfo": live_info}

    assert live_from_following(following) is None


@pytest.mark.parametrize(
    ("live_id", "last_live_id", "expected"),
    [(200, 100, True), (100, 100, False), (100, "100", False), ("100", 100, False)],
    ids=["changed", "same", "str_last", "str_live"],
)
def test_is_new_live(live_id, last_live_id, expected):
    assert is_new_live({"liveId": live_id}, last_live_id) is expected


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        ({}, True),
        ({"disable_notification": {"BOOL": False}}, True),
        ({"disable_notification": {"BOOL": True}}, False),
    ],
)
def test_should_notify(item, expected):
    assert should_notify(item) is expected


@pytest.mark.parametrize("status_code", [200, 204])
def test_delivery_update_success_resets_fail_count(status_code):
    noti = {"noti_fail_count": {"N": "4"}}
    assert delivery_update(status_code, noti, "cid", CHZZK, NOW) == {
        "last_noti_status": {"S": "SUCCESS"},
        "last_noti_at": {"S": NOW.isoformat()},
        "noti_fail_count": {"N": "0"},
        "chzzk_name": {"S": "스트리머"},
        "chzzk_image_url": {"S": "https://img"},
        "chzzk_id": {"S": "cid"},
    }


@pytest.mark.parametrize(
    ("noti", "expected"),
    [({}, "1"), ({"noti_fail_count": {"N": "2"}}, "3")],
    ids=["first", "repeated"],
)
def test_delivery_update_failure_increments_fail_count(noti, expected):
    attrs = delivery_update(404, noti, "cid", CHZZK, NOW)
    assert attrs["last_noti_status"] == {"S": "FAIL_404"}
    assert attrs["noti_fail_count"] == {"N": expected}


@pytest.mark.parametrize("prev", ["0", "2", "5"])
def test_delivery_update_network_error_is_not_counted(prev):
    attrs = delivery_update(599, {"noti_fail_count": {"N": prev}}, "cid", CHZZK, NOW)

    assert attrs["last_noti_status"] == {"S": "FAIL_599"}
    assert attrs["noti_fail_count"] == {"N": prev}
    assert "disable_notification" not in attrs


@pytest.mark.parametrize(
    ("noti", "disabled"),
    [
        ({"noti_fail_count": {"N": "1"}}, False),
        ({"noti_fail_count": {"N": "2"}}, True),
        ({"noti_fail_count": {"N": "5"}}, True),
    ],
    ids=["below", "reaches-3", "above"],
)
def test_delivery_update_disables_after_three_failures(noti, disabled):
    attrs = delivery_update(500, noti, "cid", CHZZK, NOW)
    assert ("disable_notification" in attrs) is disabled
    if disabled:
        assert attrs["disable_notification"] == {"BOOL": True}


def test_delivery_update_success_never_disables():
    attrs = delivery_update(204, {"noti_fail_count": {"N": "9"}}, "cid", CHZZK, NOW)
    assert "disable_notification" not in attrs


def test_delivery_update_missing_image_is_empty():
    chzzk = {"channel": {"channelName": "스트리머", "channelImageUrl": None}}
    assert delivery_update(200, {}, "cid", chzzk, NOW)["chzzk_image_url"] == {"S": ""}


def test_stats_accumulates_channel_results():
    stats = LiveCheckStats(index=3, total_live_channels_count=2)
    stats.add(ChannelResult(1, 2, 0))
    stats.add(ChannelResult(1, 0, 1))

    assert stats.to_dict() == {
        "index": 3,
        "total_live_channels_count": 2,
        "total_live_start_cnt": 2,
        "total_noti_send_cnt": 2,
        "total_noti_fail_cnt": 1,
    }
