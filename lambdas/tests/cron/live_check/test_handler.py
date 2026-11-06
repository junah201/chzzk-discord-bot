import importlib
import json
import logging
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from cron.live_check import adapters
from cron.live_check.logic import ChannelResult, LiveCheckStats

live_check = importlib.import_module("cron.live_check")

EVENT = {
    "resources": ["arn:aws:events:ap-northeast-2:123:rule/live_check_trigger_for_3"]
}
CHZZK_ID = "abcdef0123456789abcdef0123456789"
NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
NID_AUT = "AUT1" + "x" * 40 + "AUT9"
NID_SES = "SES1" + "y" * 200 + "SES9"


def live(**overrides):
    data = {
        "liveId": 200,
        "liveTitle": "새 방송",
        "status": "OPEN",
        "liveCategoryValue": "Just Chatting",
        "liveImageUrl": "https://example.com/live_{type}.jpg",
        "channel": {
            "channelId": CHZZK_ID,
            "channelName": "스트리머",
            "channelImageUrl": "https://example.com/profile.png",
        },
    }
    data.update(overrides)
    return data


def noti(channel_id, guild_id="1", **attrs):
    return {
        "PK": {"S": f"CHZZK#{CHZZK_ID}"},
        "SK": {"S": f"NOTI#{channel_id}"},
        "guild_id": {"S": guild_id},
        "channel_id": {"S": channel_id},
        "custom_message": {"S": ""},
        **attrs,
    }


class Fake:
    """adapters 함수를 대신하는 인메모리 가짜 I/O. 호출 기록을 남긴다."""

    def __init__(self):
        self.chzzk_items = {CHZZK_ID: {"lastLiveId": 100}}
        self.live = live()
        self.follows = []
        self.notifications = []
        self.status_by_channel = {}
        self.last_live_updates = []
        self.sent = []
        self.noti_updates = []

    def get_naver_session(self, index):
        return NID_AUT, NID_SES

    def get_follows(self, nid_aut, nid_ses, index):
        return self.follows

    def get_chzzk_item(self, chzzk_id):
        return self.chzzk_items.get(chzzk_id)

    def fetch_live(self, chzzk_id):
        if isinstance(self.live, Exception):
            raise self.live
        return self.live

    def update_last_live(self, chzzk_id, chzzk):
        self.last_live_updates.append((chzzk_id, chzzk["liveId"]))

    def query_notifications(self, chzzk_id):
        return self.notifications

    def send_notification(self, item, data):
        channel_id = item["channel_id"]["S"]
        self.sent.append((channel_id, data))
        status = self.status_by_channel.get(channel_id, 200)
        if isinstance(status, Exception):
            raise status
        return SimpleNamespace(status_code=status, text="err")

    def update_notification(self, item, attrs):
        self.noti_updates.append((item["channel_id"]["S"], attrs))


ADAPTER_NAMES = [
    name for name in vars(Fake) if not name.startswith("_") and hasattr(adapters, name)
]


@pytest.fixture
def fake(monkeypatch):
    f = Fake()
    for name in ADAPTER_NAMES:
        monkeypatch.setattr(adapters, name, getattr(f, name))
    return f


@pytest.fixture
def logs(caplog):
    caplog.set_level(logging.DEBUG)

    def entries():
        return [json.loads(r.getMessage()) for r in caplog.records]

    return entries


def log_types(logs):
    return [entry["type"] for entry in logs()]


def check():
    return live_check.check_channel(CHZZK_ID, NOW)


def test_fake_covers_every_adapter():
    assert sorted(ADAPTER_NAMES) == sorted(
        [
            "get_naver_session",
            "get_follows",
            "get_chzzk_item",
            "fetch_live",
            "update_last_live",
            "query_notifications",
            "send_notification",
            "update_notification",
        ]
    )


class TestHandler:
    def test_runs_with_index_from_rule_name(self, mocker):
        mocker.patch.object(live_check.logger, "info")
        run = mocker.patch.object(
            live_check,
            "run",
            return_value=LiveCheckStats(
                index=3,
                total_follows_count=3,
                total_live_channels_count=2,
                total_live_start_cnt=2,
                total_noti_send_cnt=2,
                total_noti_fail_cnt=1,
            ),
        )

        res = live_check.handler(EVENT, None)

        assert run.call_args.args[0] == 3
        assert res["statusCode"] == 200
        assert json.loads(res["body"]) == {
            "index": 3,
            "total_follows_count": 3,
            "total_live_channels_count": 2,
            "total_live_start_cnt": 2,
            "total_noti_send_cnt": 2,
            "total_noti_fail_cnt": 1,
        }


class TestNoNotification:
    def test_unregistered_channel(self, fake):
        fake.chzzk_items = {}

        assert check() == ChannelResult()
        assert fake.sent == []

    def test_chzzk_api_error(self, fake, logs):
        fake.live = RuntimeError("boom")

        assert check() == ChannelResult()
        assert log_types(logs) == ["GET_CHZZK_ERROR"]
        assert fake.sent == []

    def test_chzzk_returns_nothing(self, fake):
        fake.live = None
        fake.notifications = [noti("10")]

        assert check() == ChannelResult()
        assert fake.last_live_updates == []
        assert fake.sent == []

    @pytest.mark.parametrize("live_id", [100, "100"], ids=["int", "str"])
    def test_same_live_is_notified_once(self, fake, live_id):
        fake.live = live(liveId=live_id)
        fake.notifications = [noti("10")]

        assert check() == ChannelResult()
        assert fake.sent == []


class TestNewLive:
    def test_updates_last_live(self, fake):
        assert check() == ChannelResult(1, 0, 0)
        assert fake.last_live_updates == [(CHZZK_ID, 200)]

    def test_sends_to_every_notification(self, fake):
        fake.notifications = [noti("10", "1"), noti("11", "2")]

        assert check() == ChannelResult(1, 2, 0)
        assert [channel_id for channel_id, _ in fake.sent] == ["10", "11"]

    def test_skips_disabled_notification(self, fake):
        fake.notifications = [
            noti("10", disable_notification={"BOOL": True}),
            noti("11"),
        ]

        assert check() == ChannelResult(1, 1, 0)
        assert [channel_id for channel_id, _ in fake.sent] == ["11"]
        assert [channel_id for channel_id, _ in fake.noti_updates] == ["11"]

    def test_message_uses_custom_message_and_now(self, fake):
        fake.notifications = [noti("10", custom_message={"S": "@everyone"})]

        check()

        [(_, data)] = fake.sent
        assert data["content"] == "@everyone"
        assert data["embeds"][0]["timestamp"] == NOW.isoformat()

    def test_missing_custom_message_is_empty(self, fake):
        item = noti("10")
        del item["custom_message"]
        fake.notifications = [item]

        check()

        assert fake.sent[0][1]["content"] == ""


class TestDeliveryResult:
    def test_mixed_results_are_counted_and_recorded(self, fake, logs):
        fake.notifications = [noti("10"), noti("11"), noti("12")]
        fake.status_by_channel = {"10": 204, "11": 500, "12": 404}

        assert check() == ChannelResult(1, 1, 2)
        statuses = {
            channel_id: attrs["last_noti_status"]["S"]
            for channel_id, attrs in fake.noti_updates
        }
        assert statuses == {"10": "SUCCESS", "11": "FAIL_500", "12": "FAIL_404"}
        assert {attrs["last_noti_at"]["S"] for _, attrs in fake.noti_updates} == {
            NOW.isoformat()
        }
        assert [t for t in log_types(logs) if t.startswith("DISCORD_")] == [
            "DISCORD_MESSAGE_SEND_SUCCESS",
            "DISCORD_MESSAGE_SEND_FAIL",
            "DISCORD_CHANNEL_NOT_FOUND",
        ]

    def test_send_exception_stops_remaining_notifications(self, fake):
        # 현재 동작: 전송 중 예상하지 못한 예외가 나면 그대로 올라가서 남은 알림을 보내지 않는다.
        # lastLiveId는 이미 갱신된 뒤라 다음 실행에서도 이 방송은 다시 보내지 않는다.
        fake.notifications = [noti("10"), noti("11")]
        fake.status_by_channel = {"10": ConnectionError("refused")}

        with pytest.raises(ConnectionError):
            check()

        assert len(fake.sent) == 1
        assert fake.last_live_updates == [(CHZZK_ID, 200)]


class TestRun:
    def test_checks_only_live_channels_and_sums_results(self, fake, mocker):
        fake.follows = [
            {"channel": {"channelId": "a"}, "streamer": {"openLive": True}},
            {"channel": {"channelId": "b"}, "streamer": {"openLive": False}},
            {"channel": {"channelId": "c"}, "streamer": {"openLive": True}},
        ]
        check_channel = mocker.patch.object(
            live_check,
            "check_channel",
            side_effect=[ChannelResult(1, 2, 0), ChannelResult(1, 0, 1)],
        )

        stats = live_check.run(3, NOW)

        assert [c.args for c in check_channel.call_args_list] == [
            ("a", NOW),
            ("c", NOW),
        ]
        assert stats.to_dict() == {
            "index": 3,
            "total_follows_count": 3,
            "total_live_channels_count": 2,
            "total_live_start_cnt": 2,
            "total_noti_send_cnt": 2,
            "total_noti_fail_cnt": 1,
        }

    def test_one_channel_error_does_not_stop_others(self, fake, mocker, logs):
        fake.follows = [
            {"channel": {"channelId": "a"}, "streamer": {"openLive": True}},
            {"channel": {"channelId": "b"}, "streamer": {"openLive": True}},
        ]
        mocker.patch.object(
            live_check,
            "check_channel",
            side_effect=[RuntimeError("boom"), ChannelResult(1, 1, 0)],
        )

        stats = live_check.run(3, NOW)

        assert (stats.total_live_start_cnt, stats.total_noti_send_cnt) == (1, 1)
        assert "SEND_NOTIFICATION_ERROR" in log_types(logs)

    def test_session_cookies_are_masked_in_logs(self, fake, logs, caplog):
        live_check.run(3, NOW)

        [start] = [e for e in logs() if e["type"] == "LIVE_CHECK_START"]
        assert (start["NID_AUT"], start["NID_SES"]) == ("AUT1...AUT9", "SES1...SES9")
        assert NID_AUT not in caplog.text
        assert NID_SES not in caplog.text

    def test_logs_result_for_weekly_report(self, fake, logs):
        live_check.run(3, NOW)

        [result] = [e for e in logs() if e["type"] == "LIVE_CHECK_RESULT"]
        assert result["index"] == 3
        assert {
            "total_live_start_cnt",
            "total_noti_send_cnt",
            "total_noti_fail_cnt",
            "total_follows_count",
        } <= result.keys()
