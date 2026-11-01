import json

import pytest
import requests
import responses
from shared import notification_dispatcher
from shared.notification_dispatcher import (
    DEFAULT_EMBED_COLOR,
    get_embed_color,
    get_embed_fields,
    is_valid_webhook_url,
    parse_embed_color,
    send_notification_message,
)


class TestIsValidWebhookUrl:
    @pytest.mark.parametrize(
        "url",
        [
            "https://discord.com/api/webhooks/123456789/abc-DEF_123",
            "https://discordapp.com/api/webhooks/1/token",
        ],
        ids=["discord.com", "discordapp.com"],
    )
    def test_accepts_discord_webhook(self, url):
        assert is_valid_webhook_url(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "http://discord.com/api/webhooks/1/token",
            "https://ptb.discord.com/api/webhooks/1/token",
            "https://example.com/api/webhooks/1/token",
            "https://discord.com.evil.com/api/webhooks/1/token",
            "https://discord.com/api/webhooks/abc/token",
            "https://discord.com/api/webhooks/1/",
            "https://discord.com/api/webhooks/1/token?wait=true",
            "https://discord.com/api/webhooks/1/token/slack",
            "https://discord.com/api/webhooks/1/token\n",
            " https://discord.com/api/webhooks/1/token",
            "",
        ],
        ids=[
            "http",
            "subdomain",
            "other-domain",
            "lookalike-domain",
            "non-numeric-id",
            "missing-token",
            "query-string",
            "extra-path",
            "trailing-newline",
            "leading-space",
            "empty",
        ],
    )
    def test_rejects_invalid_url(self, url):
        assert is_valid_webhook_url(url) is False


class TestParseEmbedColor:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("#AABBCC", 0xAABBCC),
            ("#aabbcc", 0xAABBCC),
            ("#000000", 0),
            ("#FFFFFF", 0xFFFFFF),
            ("  #00FF00  ", 0x00FF00),
            ("0", 0),
            ("16777215", 0xFFFFFF),
            ("65280", 0x00FF00),
        ],
        ids=[
            "hex-upper",
            "hex-lower",
            "hex-min",
            "hex-max",
            "hex-padded",
            "dec-min",
            "dec-max",
            "dec",
        ],
    )
    def test_valid_values(self, value, expected):
        assert parse_embed_color(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "   ",
            "#ABC",
            "#GGGGGG",
            "AABBCC",
            "0x00FF00",
            "16777216",
            "-1",
            "1.5",
            "#AABBCCDD",
        ],
        ids=[
            "empty",
            "blank",
            "short-hex",
            "non-hex",
            "no-hash",
            "0x-prefix",
            "dec-over-max",
            "negative",
            "float",
            "hex-alpha",
        ],
    )
    def test_invalid_values_return_none(self, value):
        assert parse_embed_color(value) is None


class TestGetEmbedColor:
    @staticmethod
    def item(active=None, color=None):
        item = {}
        if active is not None:
            item["is_subscription_active"] = {"BOOL": active}
        if color is not None:
            item["embed_color"] = {"S": color}
        return item

    def test_default_color_value(self):
        assert DEFAULT_EMBED_COLOR == 0x02E895

    def test_active_subscription_uses_custom_color(self):
        assert get_embed_color(self.item(active=True, color="#FF0000")) == 0xFF0000

    def test_active_subscription_with_invalid_color_uses_default(self):
        assert (
            get_embed_color(self.item(active=True, color="red")) == DEFAULT_EMBED_COLOR
        )

    def test_inactive_subscription_ignores_custom_color(self):
        assert (
            get_embed_color(self.item(active=False, color="#FF0000"))
            == DEFAULT_EMBED_COLOR
        )

    @pytest.mark.parametrize(
        "item",
        [
            {},
            {"embed_color": {"S": "#FF0000"}},
            {"is_subscription_active": {"BOOL": True}},
        ],
        ids=["empty", "color-without-subscription-flag", "subscription-without-color"],
    )
    def test_missing_attributes_use_default(self, item):
        assert get_embed_color(item) == DEFAULT_EMBED_COLOR


class TestGetEmbedFields:
    CATEGORY = {"name": "카테고리", "value": "Just Chatting"}

    @staticmethod
    def chzzk(**overrides):
        return {"liveCategoryValue": "Just Chatting", **overrides}

    def test_tags_are_shown_when_disable_tag_is_missing(self):
        fields = get_embed_fields(self.chzzk(tags=["게임", "소통"]), {})

        assert fields == [self.CATEGORY, {"name": "태그", "value": "`게임` `소통`"}]

    def test_disable_tag_false_shows_tags(self):
        fields = get_embed_fields(
            self.chzzk(tags=["게임"]), {"disable_tag": {"BOOL": False}}
        )

        assert fields == [self.CATEGORY, {"name": "태그", "value": "`게임`"}]

    def test_disable_tag_hides_tags(self):
        fields = get_embed_fields(
            self.chzzk(tags=["게임"]), {"disable_tag": {"BOOL": True}}
        )

        assert fields == [self.CATEGORY]

    @pytest.mark.parametrize(
        "chzzk",
        [{}, {"tags": None}, {"tags": []}, {"tags": [""]}],
        ids=["missing", "none", "empty", "blank-tag"],
    )
    def test_no_tags_omits_field(self, chzzk):
        assert get_embed_fields(self.chzzk(**chzzk), {}) == [self.CATEGORY]

    def test_tag_value_is_capped_at_discord_field_limit(self):
        fields = get_embed_fields(self.chzzk(tags=["가" * 100] * 20), {})

        assert len(fields[1]["value"]) == 1024


WEBHOOK_URL = "https://discord.com/api/webhooks/1/token"
MESSAGE = {"content": "방송 시작", "embeds": []}


class TestSendNotificationMessage:
    @pytest.fixture
    def send_message(self, mocker):
        return mocker.patch.object(
            notification_dispatcher,
            "send_message",
            return_value=mocker.Mock(status_code=200),
        )

    @pytest.fixture
    def send_webhook(self, mocker):
        return mocker.patch.object(
            notification_dispatcher,
            "_send_webhook",
            return_value=mocker.Mock(status_code=204, text=""),
        )

    @pytest.fixture
    def log_error(self, mocker):
        return mocker.patch.object(notification_dispatcher.logger, "error")

    @staticmethod
    def send(notification_item):
        return send_notification_message(
            guild_id="10",
            channel_id="20",
            data=MESSAGE,
            notification_item=notification_item,
        )

    @pytest.mark.parametrize(
        "item",
        [
            {},
            {"webhook_url": {"S": WEBHOOK_URL}},
            {
                "is_subscription_active": {"BOOL": False},
                "webhook_url": {"S": WEBHOOK_URL},
            },
            {"is_subscription_active": {"BOOL": True}},
            {"is_subscription_active": {"BOOL": True}, "webhook_url": {"S": ""}},
        ],
        ids=[
            "no-subscription",
            "webhook-without-subscription-flag",
            "inactive-subscription-with-webhook",
            "active-subscription-without-webhook",
            "active-subscription-with-empty-webhook",
        ],
    )
    def test_sends_bot_message_without_active_webhook(
        self, send_message, send_webhook, item
    ):
        res = self.send(item)

        send_message.assert_called_once_with(channel_id="20", data=MESSAGE)
        send_webhook.assert_not_called()
        assert res is send_message.return_value

    def test_active_subscription_with_webhook_sends_webhook(
        self, send_message, send_webhook, log_error
    ):
        res = self.send(
            {
                "is_subscription_active": {"BOOL": True},
                "webhook_url": {"S": WEBHOOK_URL},
            }
        )

        send_webhook.assert_called_once_with(WEBHOOK_URL, MESSAGE)
        send_message.assert_not_called()
        log_error.assert_not_called()
        assert res is send_webhook.return_value

    @pytest.mark.parametrize("status_code", [200, 204])
    def test_webhook_success_is_not_logged(
        self, mocker, send_message, send_webhook, log_error, status_code
    ):
        send_webhook.return_value = mocker.Mock(status_code=status_code, text="")

        self.send(
            {
                "is_subscription_active": {"BOOL": True},
                "webhook_url": {"S": WEBHOOK_URL},
            }
        )

        log_error.assert_not_called()

    @pytest.mark.parametrize("status_code", [400, 404, 429, 599])
    def test_webhook_failure_is_logged_and_returned(
        self, mocker, send_message, send_webhook, log_error, status_code
    ):
        failed = mocker.Mock(status_code=status_code, text="Unknown Webhook")
        send_webhook.return_value = failed

        res = self.send(
            {
                "is_subscription_active": {"BOOL": True},
                "webhook_url": {"S": WEBHOOK_URL},
            }
        )

        assert res is failed
        # 의도한 동작: 웹훅이 실패해도 봇 메시지로 대체 전송하지 않는다.
        send_message.assert_not_called()
        log_error.assert_called_once()
        assert json.loads(log_error.call_args.args[0]) == {
            "type": "DISCORD_WEBHOOK_INVALID",
            "guild_id": "10",
            "channel_id": "20",
            "status_code": status_code,
            "response_text": "Unknown Webhook",
        }


class TestSendWebhook:
    @pytest.fixture
    def log_error(self, mocker):
        return mocker.patch.object(notification_dispatcher.logger, "error")

    @pytest.mark.parametrize("status", [200, 204])
    def test_success(self, mocker, mock_requests, log_error, status):
        mock_requests.add(responses.POST, WEBHOOK_URL, status=status)
        spy = mocker.spy(notification_dispatcher.session, "post")

        res = notification_dispatcher._send_webhook(WEBHOOK_URL, MESSAGE)

        assert res.status_code == status
        request = mock_requests.calls[0].request
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.body) == MESSAGE
        assert spy.call_args.kwargs["timeout"] == 5
        log_error.assert_not_called()

    @pytest.mark.parametrize("status", [400, 404, 429, 500])
    def test_http_error_is_returned_as_is(self, mock_requests, log_error, status):
        mock_requests.add(
            responses.POST,
            WEBHOOK_URL,
            json={"message": "Unknown Webhook"},
            status=status,
        )

        res = notification_dispatcher._send_webhook(WEBHOOK_URL, MESSAGE)

        assert res.status_code == status
        log_error.assert_not_called()

    @pytest.mark.parametrize(
        "error",
        [
            requests.exceptions.ReadTimeout("read timed out"),
            requests.exceptions.ConnectionError("connection refused"),
            requests.exceptions.InvalidURL("invalid url"),
        ],
        ids=["timeout", "connection-error", "invalid-url"],
    )
    def test_request_exception_returns_599(self, mock_requests, log_error, error):
        mock_requests.add(responses.POST, WEBHOOK_URL, body=error)

        res = notification_dispatcher._send_webhook(WEBHOOK_URL, MESSAGE)

        assert isinstance(res, requests.Response)
        assert res.status_code == 599
        assert res.text == str(error)
        assert json.loads(log_error.call_args.args[0]) == {
            "type": "DISCORD_WEBHOOK_REQUEST_ERROR",
            "error": str(error),
        }

    def test_non_request_exception_propagates(self, mock_requests):
        # 현재 동작: requests 예외가 아닌 오류는 599로 바꾸지 않고 그대로 던진다.
        mock_requests.add(responses.POST, WEBHOOK_URL, body=RuntimeError("boom"))

        with pytest.raises(RuntimeError):
            notification_dispatcher._send_webhook(WEBHOOK_URL, MESSAGE)
