import importlib
import json
from datetime import datetime

import pytest
import requests
from shared.discord import BUTTON_STYLE, COMPONENT_TYPE
from shared.notification_dispatcher import DEFAULT_EMBED_COLOR

live_check = importlib.import_module("cron.live_check")

CHZZK_ID = "abcdef0123456789abcdef0123456789"
LIVE_URL = f"https://chzzk.naver.com/live/{CHZZK_ID}"
CHANNEL_IMAGE = "https://example.com/profile.png"


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
            "channelImageUrl": CHANNEL_IMAGE,
        },
    }
    data.update(overrides)
    return data


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(live_check, "dynamodb", dynamodb_table.client)
    mocker.patch.object(live_check, "table", dynamodb_table.table)
    return dynamodb_table


@pytest.fixture
def get_chzzk(mocker):
    return mocker.patch.object(live_check, "get_chzzk", return_value=live())


@pytest.fixture
def send(mocker):
    return mocker.patch.object(
        live_check,
        "send_notification_message",
        return_value=mocker.Mock(status_code=200, text=""),
    )


@pytest.fixture
def log_error(mocker):
    return mocker.patch.object(live_check.logger, "error")


def put_chzzk(table, chzzk_id=CHZZK_ID, last_live_id=100):
    table.put_item(
        Item={
            "PK": f"CHZZK#{chzzk_id}",
            "SK": f"CHZZK#{chzzk_id}",
            "type": "CHZZK",
            "channelId": chzzk_id,
            "channelName": "옛 이름",
            "lastLiveId": last_live_id,
            "lastLiveTitle": "지난 방송",
            "index": 3,
        }
    )


def put_noti(table, channel_id, guild_id="1", chzzk_id=CHZZK_ID, **attrs):
    table.put_item(
        Item={
            "PK": f"CHZZK#{chzzk_id}",
            "SK": f"NOTI#{channel_id}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": channel_id,
            "chzzk_id": chzzk_id,
            "chzzk_name": "옛 이름",
            "custom_message": "",
            "disable_embed": False,
            "disable_button": False,
            "disable_notification": False,
            "index": -1,
            **attrs,
        }
    )


def get_item(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk})["Item"]


def get_chzzk_item(table):
    return get_item(table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}")


def get_noti(table, channel_id):
    return get_item(table, f"CHZZK#{CHZZK_ID}", f"NOTI#{channel_id}")


def sent_data(send, channel_id):
    for c in send.call_args_list:
        if c.kwargs["channel_id"] == channel_id:
            return c.kwargs["data"]
    raise AssertionError(f"{channel_id}로 보낸 메시지가 없습니다.")


def logged_types(log_mock):
    return [json.loads(c.args[0])["type"] for c in log_mock.call_args_list]


class TestNoNotification:
    def test_unregistered_channel(self, get_chzzk, send, log_error):
        assert live_check.send_notification(CHZZK_ID, 3) == (0, 0, 0)
        assert logged_types(log_error) == ["GET_DYNAMODB_ERROR"]
        get_chzzk.assert_not_called()
        send.assert_not_called()

    def test_chzzk_api_error(self, ddb, get_chzzk, send, log_error):
        put_chzzk(ddb.table)
        get_chzzk.side_effect = RuntimeError("boom")

        assert live_check.send_notification(CHZZK_ID, 3) == (0, 0, 0)
        assert logged_types(log_error) == ["GET_CHZZK_ERROR"]
        send.assert_not_called()

    def test_chzzk_returns_nothing(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10")
        get_chzzk.return_value = None

        assert live_check.send_notification(CHZZK_ID, 3) == (0, 0, 0)
        assert get_chzzk_item(ddb.table)["lastLiveId"] == 100
        send.assert_not_called()

    @pytest.mark.parametrize("live_id", [100, "100"], ids=["int", "str"])
    def test_same_live_is_notified_once(self, ddb, get_chzzk, send, live_id):
        put_chzzk(ddb.table, last_live_id=100)
        put_noti(ddb.table, "10")
        get_chzzk.return_value = live(liveId=live_id)

        assert live_check.send_notification(CHZZK_ID, 3) == (0, 0, 0)
        send.assert_not_called()

    def test_get_chzzk_receives_logger(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)

        live_check.send_notification(CHZZK_ID, 3)

        get_chzzk.assert_called_once_with(CHZZK_ID, logger=live_check.logger)


class TestNewLive:
    def test_updates_last_live(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 0, 0)

        item = get_chzzk_item(ddb.table)
        assert (item["lastLiveId"], item["lastLiveTitle"]) == (200, "새 방송")
        send.assert_not_called()

    def test_sends_to_every_notification_of_channel(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", guild_id="1")
        put_noti(ddb.table, "11", guild_id="2")
        put_noti(ddb.table, "20", chzzk_id="other")

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 2, 0)

        calls = sorted(
            (c.kwargs["guild_id"], c.kwargs["channel_id"]) for c in send.call_args_list
        )
        assert calls == [("1", "10"), ("2", "11")]
        noti = send.call_args_list[0].kwargs["notification_item"]
        assert noti["SK"]["S"].startswith("NOTI#")

    def test_skips_disabled_notification(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", disable_notification=True)
        put_noti(ddb.table, "11")

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 1, 0)
        assert [c.kwargs["channel_id"] for c in send.call_args_list] == ["11"]
        assert "last_noti_status" not in get_noti(ddb.table, "10")


class TestMessage:
    def test_full_message(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", custom_message="@everyone 방송 시작!")

        live_check.send_notification(CHZZK_ID, 3)

        data = sent_data(send, "10")
        assert data["content"] == "@everyone 방송 시작!"
        (embed,) = data["embeds"]
        timestamp = embed.pop("timestamp")
        datetime.fromisoformat(timestamp)
        assert embed == {
            "title": "새 방송",
            "description": "스트리머 님이 방송을 시작했습니다.",
            "color": DEFAULT_EMBED_COLOR,
            "fields": [{"name": "카테고리", "value": "Just Chatting"}],
            "image": {"url": "https://example.com/live_1080.jpg"},
            "author": {"name": "스트리머", "url": LIVE_URL, "icon_url": CHANNEL_IMAGE},
            "footer": {"text": "chzzk.junah.dev"},
            "url": LIVE_URL,
        }
        assert data["components"] == [
            {
                "type": COMPONENT_TYPE.ACTION_ROW,
                "components": [
                    {
                        "type": COMPONENT_TYPE.BUTTON,
                        "label": "바로가기",
                        "style": BUTTON_STYLE.LINK,
                        "url": LIVE_URL,
                    }
                ],
            }
        ]

    def test_missing_custom_message_is_empty(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", custom_message=None)

        live_check.send_notification(CHZZK_ID, 3)

        assert sent_data(send, "10")["content"] == ""

    def test_disable_embed_and_button(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(
            ddb.table,
            "10",
            custom_message="알림",
            disable_embed=True,
            disable_button=True,
        )

        live_check.send_notification(CHZZK_ID, 3)

        assert sent_data(send, "10") == {"content": "알림"}

    def test_subscriber_embed_color(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", is_subscription_active=True, embed_color="#FF0000")
        put_noti(ddb.table, "11", is_subscription_active=False, embed_color="#FF0000")

        live_check.send_notification(CHZZK_ID, 3)

        assert sent_data(send, "10")["embeds"][0]["color"] == 0xFF0000
        assert sent_data(send, "11")["embeds"][0]["color"] == DEFAULT_EMBED_COLOR

    def test_image_falls_back_to_channel_image(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10")
        get_chzzk.return_value = live(liveImageUrl=None)

        live_check.send_notification(CHZZK_ID, 3)

        assert sent_data(send, "10")["embeds"][0]["image"]["url"] == CHANNEL_IMAGE

    def test_missing_images_use_defaults(self, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10")
        get_chzzk.return_value = live(
            liveImageUrl=None,
            channel={
                "channelId": CHZZK_ID,
                "channelName": "스트리머",
                "channelImageUrl": None,
            },
        )

        live_check.send_notification(CHZZK_ID, 3)

        embed = sent_data(send, "10")["embeds"][0]
        assert embed["image"]["url"] == ""
        assert embed["author"]["icon_url"].startswith(
            "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray"
        )


class TestDeliveryResult:
    @pytest.mark.parametrize("status", [200, 204])
    def test_success_resets_fail_count(self, mocker, ddb, get_chzzk, send, status):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", noti_fail_count=4, last_noti_status="FAIL_403")
        send.return_value = mocker.Mock(status_code=status, text="")

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 1, 0)

        noti = get_noti(ddb.table, "10")
        assert noti["last_noti_status"] == "SUCCESS"
        assert noti["noti_fail_count"] == 0
        assert noti["chzzk_name"] == "스트리머"
        assert noti["chzzk_image_url"] == CHANNEL_IMAGE
        assert noti["chzzk_id"] == CHZZK_ID
        datetime.fromisoformat(noti["last_noti_at"])

    @pytest.mark.parametrize(
        ("existing", "expected"), [(None, 1), (2, 3)], ids=["first", "repeated"]
    )
    def test_failure_increments_fail_count(
        self, mocker, ddb, get_chzzk, send, log_error, existing, expected
    ):
        put_chzzk(ddb.table)
        attrs = {} if existing is None else {"noti_fail_count": existing}
        put_noti(ddb.table, "10", **attrs)
        send.return_value = mocker.Mock(status_code=403, text="Missing Access")

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 0, 1)

        noti = get_noti(ddb.table, "10")
        assert noti["last_noti_status"] == "FAIL_403"
        assert noti["noti_fail_count"] == expected
        assert noti["chzzk_name"] == "스트리머"
        assert logged_types(log_error) == ["DISCORD_MESSAGE_SEND_FAIL"]

    def test_channel_not_found_is_recorded_as_failure(
        self, mocker, ddb, get_chzzk, send, log_error
    ):
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10", noti_fail_count=1)
        send.return_value = mocker.Mock(status_code=404, text="Unknown Channel")

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 0, 1)

        noti = get_noti(ddb.table, "10")
        assert noti["last_noti_status"] == "FAIL_404"
        assert noti["noti_fail_count"] == 2
        datetime.fromisoformat(noti["last_noti_at"])
        assert logged_types(log_error) == ["DISCORD_CHANNEL_NOT_FOUND"]

    def test_mixed_results_are_counted(self, mocker, ddb, get_chzzk, send):
        put_chzzk(ddb.table)
        for channel_id in ("10", "11", "12"):
            put_noti(ddb.table, channel_id)
        status_by_channel = {"10": 200, "11": 500, "12": 404}
        send.side_effect = lambda **kwargs: mocker.Mock(
            status_code=status_by_channel[kwargs["channel_id"]], text=""
        )

        assert live_check.send_notification(CHZZK_ID, 3) == (1, 1, 2)
        assert get_noti(ddb.table, "10")["last_noti_status"] == "SUCCESS"
        assert get_noti(ddb.table, "11")["last_noti_status"] == "FAIL_500"
        assert get_noti(ddb.table, "12")["last_noti_status"] == "FAIL_404"

    def test_send_exception_stops_remaining_notifications(self, ddb, get_chzzk, send):
        # 현재 동작: 전송 중 예외가 나면 그대로 올라가서 남은 알림을 보내지 않는다.
        # lastLiveId는 이미 갱신된 뒤라 다음 실행에서도 이 방송은 다시 보내지 않는다.
        put_chzzk(ddb.table)
        put_noti(ddb.table, "10")
        put_noti(ddb.table, "11")
        send.side_effect = requests.exceptions.ConnectionError("refused")

        with pytest.raises(requests.exceptions.ConnectionError):
            live_check.send_notification(CHZZK_ID, 3)

        assert send.call_count == 1
        assert get_chzzk_item(ddb.table)["lastLiveId"] == 200
