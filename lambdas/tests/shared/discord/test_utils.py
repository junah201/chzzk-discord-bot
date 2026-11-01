import importlib
import json

import pytest
import requests
import responses
from shared.discord.utils import (
    DISCORD_API_TIMEOUT_SEC,
    DISCORD_USER_GUILDS_URL,
    AdminCheckResult,
    is_admin,
)

discord_utils = importlib.import_module("shared.discord.utils")

TOKEN = "Bearer user-token"
ADMIN = 0x8
MANAGE_GUILD = 0x20


@pytest.fixture
def mock_requests():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sleep(mocker):
    return mocker.patch.object(discord_utils.time, "sleep")


@pytest.fixture
def log_error(mocker):
    return mocker.patch.object(discord_utils.logger, "error")


def add_guilds(rsps, guilds, status=200):
    rsps.add(responses.GET, DISCORD_USER_GUILDS_URL, json=guilds, status=status)


def add_rate_limited(rsps, retry_after=0.5, headers=None):
    rsps.add(
        responses.GET,
        DISCORD_USER_GUILDS_URL,
        json={"message": "You are being rate limited.", "retry_after": retry_after},
        status=429,
        headers=headers,
    )


def logged(log_mock):
    return json.loads(log_mock.call_args.args[0])


class TestPermissions:
    @pytest.mark.parametrize(
        "permissions",
        [ADMIN, ADMIN | MANAGE_GUILD, 0xFFFFFFFF],
        ids=["admin", "admin-with-others", "all"],
    )
    def test_admin_guild(self, mock_requests, permissions):
        add_guilds(mock_requests, [{"id": "123", "permissions": permissions}])

        assert is_admin("123", TOKEN) == AdminCheckResult(True, 200, "")

    @pytest.mark.parametrize(
        "permissions",
        [0, MANAGE_GUILD],
        ids=["none", "manage-guild-only"],
    )
    def test_not_admin_guild(self, mock_requests, permissions):
        add_guilds(mock_requests, [{"id": "123", "permissions": permissions}])

        assert is_admin("123", TOKEN) == AdminCheckResult(False, 200, "")

    def test_guild_not_in_list(self, mock_requests):
        add_guilds(mock_requests, [{"id": "999", "permissions": ADMIN}])

        assert is_admin("123", TOKEN) == AdminCheckResult(False, 200, "")

    def test_empty_guild_list(self, mock_requests):
        add_guilds(mock_requests, [])

        assert is_admin("123", TOKEN).is_admin is False

    def test_sends_token_with_timeout(self, mocker, mock_requests):
        add_guilds(mock_requests, [])
        spy = mocker.spy(discord_utils.requests, "get")

        is_admin("123", TOKEN)

        assert mock_requests.calls[0].request.headers["Authorization"] == TOKEN
        assert spy.call_args.kwargs["timeout"] == DISCORD_API_TIMEOUT_SEC


class TestRateLimit:
    def test_retries_after_rate_limit(self, mock_requests, sleep):
        add_rate_limited(mock_requests, retry_after=0.5)
        add_guilds(mock_requests, [{"id": "123", "permissions": ADMIN}])

        assert is_admin("123", TOKEN) == AdminCheckResult(True, 200, "")
        sleep.assert_called_once_with(0.6)
        assert len(mock_requests.calls) == 2

    def test_gives_up_after_retries(self, mocker, mock_requests, sleep):
        log_warning = mocker.patch.object(discord_utils.logger, "warning")
        for _ in range(3):
            add_rate_limited(mock_requests, retry_after=0.5)

        result = is_admin("123", TOKEN, retry=3)

        assert result.is_admin is False
        assert result.status_code == 429
        assert result.retry_after == 0.5
        assert sleep.call_count == 2
        assert len(mock_requests.calls) == 3
        assert logged(log_warning)["type"] == "DISCORD_IS_ADMIN_RATE_LIMITED"

    def test_long_retry_after_returns_immediately(self, mock_requests, sleep):
        add_rate_limited(mock_requests, retry_after=30)

        result = is_admin("123", TOKEN)

        assert (result.status_code, result.retry_after) == (429, 30)
        sleep.assert_not_called()
        assert len(mock_requests.calls) == 1

    def test_missing_retry_after_retries_immediately(self, mock_requests, sleep):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, json={"message": "x"}, status=429
        )
        add_guilds(mock_requests, [])

        is_admin("123", TOKEN)

        sleep.assert_called_once_with(0.1)

    def test_non_json_rate_limit_body_is_zero(self, mock_requests, sleep):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, body="rate limited", status=429
        )

        result = is_admin("123", TOKEN, retry=1)

        assert (result.status_code, result.retry_after) == (429, 0)
        sleep.assert_not_called()

    @pytest.mark.parametrize("retry", [0, -1])
    def test_retry_below_one_still_requests_once(self, mock_requests, retry):
        add_guilds(mock_requests, [{"id": "123", "permissions": ADMIN}])

        assert is_admin("123", TOKEN, retry=retry).is_admin is True
        assert len(mock_requests.calls) == 1


class TestHttpError:
    @pytest.mark.parametrize("status", [401, 403, 500, 502])
    def test_non_200_returns_status(self, mock_requests, sleep, log_error, status):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, json={"message": "x"}, status=status
        )

        result = is_admin("123", TOKEN)

        assert result.is_admin is False
        assert result.status_code == status
        assert result.error_message == f'HTTPError: {status} - {{"message": "x"}}'
        assert len(mock_requests.calls) == 1
        sleep.assert_not_called()
        assert logged(log_error) == {
            "type": "DISCORD_IS_ADMIN_HTTP_ERROR",
            "guild_id": "123",
            "status_code": status,
            "text": '{"message": "x"}',
        }

    def test_token_is_not_logged(self, mock_requests, log_error):
        mock_requests.add(responses.GET, DISCORD_USER_GUILDS_URL, status=401)

        is_admin("123", TOKEN)

        assert "user-token" not in log_error.call_args.args[0]


class TestRequestException:
    @pytest.mark.parametrize(
        ("error", "status_code", "prefix", "log_type"),
        [
            (requests.exceptions.ReadTimeout("read"), -1, "TimeoutError", "TIMEOUT"),
            (requests.exceptions.ConnectTimeout("conn"), -1, "TimeoutError", "TIMEOUT"),
            (
                requests.exceptions.ConnectionError("refused"),
                -2,
                "ConnectionError",
                "CONNECTION_ERROR",
            ),
            (RuntimeError("boom"), -3, "UnknownError", "UNKNOWN_ERROR"),
        ],
        ids=["read-timeout", "connect-timeout", "connection-error", "unknown"],
    )
    def test_returns_negative_code(
        self, mock_requests, log_error, error, status_code, prefix, log_type
    ):
        mock_requests.add(responses.GET, DISCORD_USER_GUILDS_URL, body=error)

        result = is_admin("123", TOKEN)

        assert result.is_admin is False
        assert result.status_code == status_code
        assert result.error_message.startswith(f"{prefix}: ")
        assert len(mock_requests.calls) == 1
        assert logged(log_error)["type"] == f"DISCORD_IS_ADMIN_{log_type}"


class TestInvalidResponse:
    @pytest.mark.parametrize(
        "body",
        [
            "not-json",
            json.dumps({"message": "not a list"}),
            json.dumps([{"id": "123"}]),
            json.dumps([{"permissions": 8}]),
            json.dumps([{"id": "123", "permissions": "8"}]),
            json.dumps([{"id": "123", "permissions": None}]),
            json.dumps(["123"]),
        ],
        ids=[
            "not-json",
            "object",
            "missing-permissions",
            "missing-id",
            "string-permissions",
            "null-permissions",
            "list-of-strings",
        ],
    )
    def test_returns_minus_three(self, mock_requests, log_error, body):
        mock_requests.add(responses.GET, DISCORD_USER_GUILDS_URL, body=body, status=200)

        result = is_admin("123", TOKEN)

        assert result.is_admin is False
        assert result.status_code == -3
        assert result.error_message.startswith("InvalidResponse: ")
        assert logged(log_error)["type"] == "DISCORD_IS_ADMIN_INVALID_RESPONSE"
