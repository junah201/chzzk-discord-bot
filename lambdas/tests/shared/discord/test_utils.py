import importlib
import json

import pytest
import requests
import responses
from responses import matchers
from shared.discord.utils import (
    DISCORD_API_TIMEOUT_SEC,
    DISCORD_USER_GUILDS_URL,
    AdminCheckResult,
    AdminGuildsResult,
    get_admin_guilds,
    is_admin,
)

discord_utils = importlib.import_module("shared.discord.utils")

TOKEN = "Bearer user-token"
# v10은 permissions를 10진수 문자열로 준다.
ADMIN = str(0x8)
MANAGE_GUILD = str(0x20)


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


def guild(guild_id="123", permissions=ADMIN, **extra):
    return {
        "id": guild_id,
        "name": f"guild-{guild_id}",
        "permissions": permissions,
        **extra,
    }


def add_guilds(rsps, guilds, status=200):
    rsps.add(responses.GET, DISCORD_USER_GUILDS_URL, json=guilds, status=status)


def add_rate_limited(rsps, retry_after=0.5):
    rsps.add(
        responses.GET,
        DISCORD_USER_GUILDS_URL,
        json={"message": "You are being rate limited.", "retry_after": retry_after},
        status=429,
    )


def logged(log_mock):
    return json.loads(log_mock.call_args.args[0])


class TestGetAdminGuilds:
    @pytest.mark.parametrize(
        "permissions",
        [ADMIN, str(0x8 | 0x20), str(0xFFFFFFFF), "2251799813685247"],
        ids=["admin", "admin-with-others", "all-32bit", "all-64bit"],
    )
    def test_keeps_admin_guilds(self, mock_requests, permissions):
        admin = guild(permissions=permissions)
        add_guilds(mock_requests, [admin])

        assert get_admin_guilds(TOKEN) == AdminGuildsResult([admin], 200, "")

    @pytest.mark.parametrize(
        "permissions",
        ["0", MANAGE_GUILD, "2251799813685239"],
        ids=["none", "manage-guild-only", "64bit-without-admin"],
    )
    def test_drops_non_admin_guilds(self, mock_requests, permissions):
        add_guilds(mock_requests, [guild(permissions=permissions)])

        assert get_admin_guilds(TOKEN) == AdminGuildsResult([], 200, "")

    def test_filters_mixed_guilds_in_order(self, mock_requests):
        guilds = [
            guild("1", ADMIN),
            guild("2", MANAGE_GUILD),
            guild("3", str(0x8 | 0x20)),
        ]
        add_guilds(mock_requests, guilds)

        result = get_admin_guilds(TOKEN)

        assert [g["id"] for g in result.guilds] == ["1", "3"]

    def test_empty_guild_list(self, mock_requests):
        add_guilds(mock_requests, [])

        assert get_admin_guilds(TOKEN) == AdminGuildsResult([], 200, "")

    def test_sends_token_with_timeout_and_no_params(self, mocker, mock_requests):
        add_guilds(mock_requests, [])
        spy = mocker.spy(discord_utils.requests, "get")

        get_admin_guilds(TOKEN)

        assert mock_requests.calls[0].request.headers["Authorization"] == TOKEN
        assert mock_requests.calls[0].request.url == DISCORD_USER_GUILDS_URL
        assert spy.call_args.kwargs["timeout"] == DISCORD_API_TIMEOUT_SEC

    def test_with_counts(self, mock_requests):
        admin = guild(approximate_member_count=10, approximate_presence_count=3)
        mock_requests.add(
            responses.GET,
            DISCORD_USER_GUILDS_URL,
            json=[admin],
            match=[matchers.query_param_matcher({"with_counts": "true"})],
        )

        assert get_admin_guilds(TOKEN, with_counts=True).guilds == [admin]


class TestRateLimit:
    def test_retries_after_rate_limit(self, mock_requests, sleep):
        add_rate_limited(mock_requests, retry_after=0.5)
        add_guilds(mock_requests, [guild()])

        assert get_admin_guilds(TOKEN).guilds == [guild()]
        sleep.assert_called_once_with(0.6)
        assert len(mock_requests.calls) == 2

    def test_gives_up_after_retries(self, mocker, mock_requests, sleep):
        log_warning = mocker.patch.object(discord_utils.logger, "warning")
        for _ in range(3):
            add_rate_limited(mock_requests, retry_after=0.5)

        result = get_admin_guilds(TOKEN, retry=3)

        assert result.guilds is None
        assert (result.status_code, result.retry_after) == (429, 0.5)
        assert sleep.call_count == 2
        assert len(mock_requests.calls) == 3
        assert logged(log_warning)["type"] == "DISCORD_GET_ADMIN_GUILDS_RATE_LIMITED"

    def test_long_retry_after_returns_immediately(self, mock_requests, sleep):
        add_rate_limited(mock_requests, retry_after=30)

        result = get_admin_guilds(TOKEN)

        assert (result.status_code, result.retry_after) == (429, 30)
        sleep.assert_not_called()
        assert len(mock_requests.calls) == 1

    def test_missing_retry_after_retries_immediately(self, mock_requests, sleep):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, json={"message": "x"}, status=429
        )
        add_guilds(mock_requests, [])

        get_admin_guilds(TOKEN)

        sleep.assert_called_once_with(0.1)

    def test_non_json_rate_limit_body_is_zero(self, mock_requests, sleep):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, body="rate limited", status=429
        )

        result = get_admin_guilds(TOKEN, retry=1)

        assert (result.status_code, result.retry_after) == (429, 0)
        sleep.assert_not_called()

    @pytest.mark.parametrize("retry", [0, -1])
    def test_retry_below_one_still_requests_once(self, mock_requests, retry):
        add_guilds(mock_requests, [guild()])

        assert get_admin_guilds(TOKEN, retry=retry).status_code == 200
        assert len(mock_requests.calls) == 1


class TestHttpError:
    @pytest.mark.parametrize("status", [401, 403, 500, 502])
    def test_non_200_returns_status(self, mock_requests, sleep, log_error, status):
        mock_requests.add(
            responses.GET, DISCORD_USER_GUILDS_URL, json={"message": "x"}, status=status
        )

        result = get_admin_guilds(TOKEN)

        assert result == AdminGuildsResult(
            None, status, f'HTTPError: {status} - {{"message": "x"}}'
        )
        assert len(mock_requests.calls) == 1
        sleep.assert_not_called()
        assert logged(log_error) == {
            "type": "DISCORD_GET_ADMIN_GUILDS_HTTP_ERROR",
            "status_code": status,
            "text": '{"message": "x"}',
        }

    def test_token_is_not_logged(self, mock_requests, log_error):
        mock_requests.add(responses.GET, DISCORD_USER_GUILDS_URL, status=401)

        get_admin_guilds(TOKEN)

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

        result = get_admin_guilds(TOKEN)

        assert result.guilds is None
        assert result.status_code == status_code
        assert result.error_message.startswith(f"{prefix}: ")
        assert len(mock_requests.calls) == 1
        assert logged(log_error)["type"] == f"DISCORD_GET_ADMIN_GUILDS_{log_type}"


class TestInvalidResponse:
    @pytest.mark.parametrize(
        "body",
        [
            "not-json",
            json.dumps({"message": "not a list"}),
            json.dumps([{"id": "123"}]),
            json.dumps([{"permissions": "8"}]),
            json.dumps([{"id": "123", "permissions": "abc"}]),
            json.dumps([{"id": "123", "permissions": None}]),
            json.dumps(["123"]),
        ],
        ids=[
            "not-json",
            "object",
            "missing-permissions",
            "missing-id",
            "non-numeric-permissions",
            "null-permissions",
            "list-of-strings",
        ],
    )
    def test_returns_minus_three(self, mock_requests, log_error, body):
        mock_requests.add(responses.GET, DISCORD_USER_GUILDS_URL, body=body, status=200)

        result = get_admin_guilds(TOKEN)

        assert result.guilds is None
        assert result.status_code == -3
        assert result.error_message.startswith("InvalidResponse: ")
        assert logged(log_error)["type"] == "DISCORD_GET_ADMIN_GUILDS_INVALID_RESPONSE"


class TestIsAdmin:
    @pytest.fixture
    def get_admin_guilds_mock(self, mocker):
        return mocker.patch.object(discord_utils, "get_admin_guilds")

    def test_admin_when_guild_is_in_admin_guilds(self, get_admin_guilds_mock):
        get_admin_guilds_mock.return_value = AdminGuildsResult(
            [guild("1"), guild("123")], 200
        )

        assert is_admin("123", TOKEN) == AdminCheckResult(True, 200, "")
        get_admin_guilds_mock.assert_called_once_with(TOKEN, retry=3)

    @pytest.mark.parametrize(
        "guilds", [[], [guild("999")]], ids=["no-admin-guilds", "other-guild"]
    )
    def test_not_admin_when_guild_is_missing(self, get_admin_guilds_mock, guilds):
        get_admin_guilds_mock.return_value = AdminGuildsResult(guilds, 200)

        assert is_admin("123", TOKEN) == AdminCheckResult(False, 200, "")

    def test_passes_retry(self, get_admin_guilds_mock):
        get_admin_guilds_mock.return_value = AdminGuildsResult([], 200)

        is_admin("123", TOKEN, retry=1)

        get_admin_guilds_mock.assert_called_once_with(TOKEN, retry=1)

    @pytest.mark.parametrize(
        "failure",
        [
            AdminGuildsResult(None, 429, "RateLimited: {}", 2.5),
            AdminGuildsResult(None, -1, "TimeoutError: x"),
            AdminGuildsResult(None, 401, "HTTPError: 401 - x"),
        ],
        ids=["rate-limited", "timeout", "http-error"],
    )
    def test_failure_is_passed_through(self, get_admin_guilds_mock, failure):
        get_admin_guilds_mock.return_value = failure

        assert is_admin("123", TOKEN) == AdminCheckResult(
            False, failure.status_code, failure.error_message, failure.retry_after
        )

    def test_end_to_end_with_http(self, mock_requests):
        add_guilds(mock_requests, [guild("123", ADMIN), guild("456", MANAGE_GUILD)])

        assert is_admin("123", TOKEN).is_admin is True

    def test_end_to_end_non_admin_with_http(self, mock_requests):
        add_guilds(mock_requests, [guild("123", ADMIN), guild("456", MANAGE_GUILD)])

        assert is_admin("456", TOKEN).is_admin is False
