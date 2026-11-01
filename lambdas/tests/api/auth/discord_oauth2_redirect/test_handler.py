import importlib
import json
from urllib.parse import parse_qs

import pytest
from shared.discord.utils import DISCORD_API_BASE_URL

discord_oauth2_redirect = importlib.import_module("api.auth.discord_oauth2_redirect")

TOKEN_URL = f"{DISCORD_API_BASE_URL}/oauth2/token"


def body_of(res):
    return json.loads(res["body"])


class TestOAuth2Redirect:
    def call(self, code="code-123", origin=None):
        headers = {"origin": origin} if origin else {}
        body = {"code": code} if code else {}
        return discord_oauth2_redirect.handler(
            {"headers": headers, "body": json.dumps(body)}, None
        )

    @pytest.mark.parametrize(
        ("origin", "redirect_uri"),
        [
            ("http://localhost:3000", "http://localhost:3000/login/callback"),
            (
                "https://dev.chzzk.junah.dev",
                "https://dev.chzzk.junah.dev/login/callback",
            ),
            ("https://chzzk.junah.dev", "https://chzzk.junah.dev/login/callback"),
            (None, "https://junah.dev/login/callback"),
        ],
        ids=["localhost", "dev", "prod", "unknown"],
    )
    def test_redirect_uri_follows_origin(self, mock_requests, origin, redirect_uri):
        mock_requests.post(TOKEN_URL, json={"access_token": "a"})

        res = self.call(origin=origin)

        assert res["statusCode"] == 200
        sent = parse_qs(mock_requests.calls[0].request.body)
        assert sent["redirect_uri"] == [redirect_uri]
        assert sent["code"] == ["code-123"]
        assert sent["grant_type"] == ["authorization_code"]

    def test_returns_only_public_token_fields(self, mock_requests):
        mock_requests.post(
            TOKEN_URL,
            json={
                "access_token": "access",
                "refresh_token": "refresh",
                "token_type": "Bearer",
                "scope": "identify guilds",
                "expires_in": 604800,
            },
        )

        res = self.call(origin="https://chzzk.junah.dev")

        # refresh_token은 프론트엔드로 내려보내지 않는다.
        assert body_of(res) == {
            "access_token": "access",
            "scope": "identify guilds",
            "expires_in": 604800,
        }

    def test_missing_code_is_400(self):
        res = self.call(code=None)

        assert res["statusCode"] == 400

    def test_rejected_code_is_401(self, mock_requests):
        mock_requests.post(TOKEN_URL, status=400, json={"error": "invalid_grant"})

        res = self.call()

        assert res["statusCode"] == 401
        assert body_of(res)["code"] == "UNAUTHORIZED"
