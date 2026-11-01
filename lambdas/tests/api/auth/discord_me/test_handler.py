import importlib
import json

from responses import matchers
from shared.discord.utils import DISCORD_API_BASE_URL

discord_me = importlib.import_module("api.auth.discord_me")

ME_URL = f"{DISCORD_API_BASE_URL}/users/@me"


def body_of(res):
    return json.loads(res["body"])


class TestDiscordMe:
    def test_returns_discord_user(self, mock_requests):
        user = {"id": "1", "username": "치직"}
        mock_requests.get(
            ME_URL,
            json=user,
            match=[matchers.header_matcher({"Authorization": "Bearer user-token"})],
        )

        res = discord_me.handler(
            {"headers": {"Authorization": "Bearer user-token"}}, None
        )

        assert res["statusCode"] == 200
        assert body_of(res) == user

    def test_missing_token_is_401(self):
        res = discord_me.handler({"headers": {}}, None)

        assert res["statusCode"] == 401
        assert body_of(res)["code"] == "UNAUTHORIZED"

    def test_rejected_token_is_401(self, mock_requests):
        mock_requests.get(ME_URL, status=401, json={"message": "401: Unauthorized"})

        res = discord_me.handler({"headers": {"Authorization": "Bearer bad"}}, None)

        assert res["statusCode"] == 401
        assert body_of(res)["code"] == "UNAUTHORIZED"
