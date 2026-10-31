import pytest
from shared.notification_dispatcher import (
    DEFAULT_EMBED_COLOR,
    get_embed_color,
    is_valid_webhook_url,
    parse_embed_color,
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
