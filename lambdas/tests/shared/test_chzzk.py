import json

import pytest
import requests
import responses
from shared import chzzk
from shared.chzzk import (
    CHZZK_FOLLOW_URL,
    follow_chzzk_channel,
    get_chzzk,
    unfollow_chzzk_channel,
)

CHZZK_ID = "abcdef0123456789abcdef0123456789"
LIVE_DETAIL_URL = (
    f"https://api.chzzk.naver.com/service/v2/channels/{CHZZK_ID}/live-detail"
)
FOLLOW_URL = CHZZK_FOLLOW_URL.format(channel_id=CHZZK_ID)
LIVE = {
    "liveId": 123,
    "liveTitle": "방송 제목",
    "status": "OPEN",
    "channel": {"channelId": CHZZK_ID, "channelName": "스트리머"},
}


@pytest.fixture
def logger(mocker):
    return mocker.Mock()


def logged_types(logger):
    return [json.loads(c.args[0])["type"] for c in logger.error.call_args_list]


class TestGetChzzk:
    def test_returns_content(self, mock_requests, logger):
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, json={"content": LIVE})

        assert get_chzzk(CHZZK_ID, logger=logger) == LIVE
        logger.error.assert_not_called()

    def test_sends_user_agent_with_timeout(self, mocker, mock_requests):
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, json={"content": LIVE})
        spy = mocker.spy(chzzk.requests, "get")

        get_chzzk(CHZZK_ID)

        assert mock_requests.calls[0].request.headers["User-Agent"]
        assert spy.call_args.kwargs["timeout"] == 1

    def test_never_broadcast_returns_none(self, mock_requests, logger):
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, json={"content": None})

        assert get_chzzk(CHZZK_ID, logger=logger) is None
        logger.error.assert_not_called()

    @pytest.mark.parametrize("status", [404, 500])
    def test_non_200_returns_none(self, mock_requests, logger, status):
        mock_requests.add(
            responses.GET, LIVE_DETAIL_URL, json={"message": "x"}, status=status
        )

        assert get_chzzk(CHZZK_ID, logger=logger) is None
        assert logged_types(logger) == ["CHZZK_INVALID_RESPONSE"]
        assert json.loads(logger.error.call_args.args[0])["status_code"] == status
        assert len(mock_requests.calls) == 1

    def test_channel_id_with_slash_skips_request(self, mock_requests, logger):
        assert get_chzzk("https://chzzk.naver.com/abc", logger=logger) is None
        assert logged_types(logger) == ["INVALID_CHZZK_CHANNEL_ID"]
        assert len(mock_requests.calls) == 0

    @pytest.mark.parametrize(
        ("error", "log_type"),
        [
            (requests.exceptions.ReadTimeout("read"), "CHZZK_REQUEST_TIMEOUT"),
            (requests.exceptions.ConnectionError("refused"), "CHZZK_REQUEST_ERROR"),
        ],
        ids=["timeout", "connection-error"],
    )
    def test_retries_after_request_error(self, mock_requests, logger, error, log_type):
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, body=error)
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, json={"content": LIVE})

        assert get_chzzk(CHZZK_ID, logger=logger) == LIVE
        assert len(mock_requests.calls) == 2
        assert logged_types(logger) == [log_type]

    def test_all_retries_fail_returns_none(self, mock_requests, logger):
        for _ in range(3):
            mock_requests.add(
                responses.GET,
                LIVE_DETAIL_URL,
                body=requests.exceptions.ReadTimeout("read"),
            )

        assert get_chzzk(CHZZK_ID, logger=logger, retry=3) is None
        assert len(mock_requests.calls) == 3
        assert logged_types(logger) == ["CHZZK_REQUEST_TIMEOUT"] * 3 + [
            "CHZZK_REQUEST_FAILED"
        ]

    def test_works_without_logger(self, mock_requests):
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, status=404)

        assert get_chzzk(CHZZK_ID) is None
        assert get_chzzk("a/b") is None

    @pytest.mark.parametrize(
        "body",
        [json.dumps({"code": 200}), "not-json"],
        ids=["missing-content-key", "not-json"],
    )
    def test_malformed_200_response_raises(self, mock_requests, body):
        # 현재 동작: 200인데 content 키가 없거나 JSON이 아니면 None이 아니라 예외가 그대로 올라간다.
        mock_requests.add(responses.GET, LIVE_DETAIL_URL, body=body, status=200)

        with pytest.raises((KeyError, ValueError)):
            get_chzzk(CHZZK_ID)


class TestFollowRequest:
    @pytest.fixture
    def log_error(self, mocker):
        return mocker.patch.object(chzzk.logger, "error")

    @pytest.mark.parametrize(
        ("func", "method"),
        [(follow_chzzk_channel, "POST"), (unfollow_chzzk_channel, "DELETE")],
        ids=["follow", "unfollow"],
    )
    def test_success(self, mock_requests, log_error, func, method):
        mock_requests.add(method, FOLLOW_URL, json={"code": 200})

        assert func(CHZZK_ID, "aut", "ses") == (True, 200, "")
        request = mock_requests.calls[0].request
        assert request.method == method
        assert request.headers["Cookie"] == "NID_AUT=aut; NID_SES=ses"
        assert request.headers["User-Agent"]
        log_error.assert_not_called()

    def test_uses_timeout(self, mocker, mock_requests):
        mock_requests.add(responses.POST, FOLLOW_URL, json={})
        spy = mocker.spy(chzzk.requests, "request")

        follow_chzzk_channel(CHZZK_ID, "aut", "ses")

        assert spy.call_args.kwargs["timeout"] == 3

    @pytest.mark.parametrize(
        ("error", "status_code", "prefix", "log_type"),
        [
            (
                requests.exceptions.ReadTimeout("read"),
                -1,
                "TimeoutError",
                "CHZZK_FOLLOW_TIMEOUT",
            ),
            (
                requests.exceptions.ConnectTimeout("conn"),
                -1,
                "TimeoutError",
                "CHZZK_FOLLOW_TIMEOUT",
            ),
            (
                requests.exceptions.ConnectionError("refused"),
                -2,
                "ConnectionError",
                "CHZZK_FOLLOW_CONNECTION_ERROR",
            ),
            (RuntimeError("boom"), -3, "UnknownError", "CHZZK_FOLLOW_UNKNOWN_ERROR"),
        ],
        ids=["read-timeout", "connect-timeout", "connection-error", "unknown"],
    )
    def test_request_exception(
        self, mock_requests, log_error, error, status_code, prefix, log_type
    ):
        mock_requests.add(responses.POST, FOLLOW_URL, body=error)

        ok, code, message = follow_chzzk_channel(CHZZK_ID, "aut", "ses")

        assert (ok, code) == (False, status_code)
        assert message.startswith(f"{prefix}: ")
        assert json.loads(log_error.call_args.args[0])["type"] == log_type

    def test_http_error_with_json_message(self, mock_requests, log_error):
        mock_requests.add(
            responses.POST,
            FOLLOW_URL,
            json={"code": 400, "message": "최대 팔로우 수를 초과했습니다."},
            status=400,
        )

        assert follow_chzzk_channel(CHZZK_ID, "aut", "ses") == (
            False,
            400,
            "최대 팔로우 수를 초과했습니다.",
        )
        assert json.loads(log_error.call_args.args[0]) == {
            "type": "CHZZK_FOLLOW_HTTP_ERROR",
            "chzzk_id": CHZZK_ID,
            "status_code": 400,
            "text": mock_requests.calls[0].response.text,
        }

    def test_http_error_json_without_message(self, mock_requests, log_error):
        mock_requests.add(responses.DELETE, FOLLOW_URL, json={"code": 403}, status=403)

        assert unfollow_chzzk_channel(CHZZK_ID, "aut", "ses") == (
            False,
            403,
            "HTTPError: 403",
        )
        assert (
            json.loads(log_error.call_args.args[0])["type"]
            == "CHZZK_UNFOLLOW_HTTP_ERROR"
        )

    def test_http_error_non_json(self, mock_requests, log_error):
        mock_requests.add(responses.POST, FOLLOW_URL, body="Bad Gateway", status=502)

        assert follow_chzzk_channel(CHZZK_ID, "aut", "ses") == (
            False,
            502,
            "HTTPError: 502 - Bad Gateway",
        )

    def test_session_cookies_are_not_logged(self, mock_requests, log_error):
        mock_requests.add(responses.POST, FOLLOW_URL, body="error", status=401)

        follow_chzzk_channel(CHZZK_ID, "secret-aut", "secret-ses")

        logged = log_error.call_args.args[0]
        assert "secret-aut" not in logged
        assert "secret-ses" not in logged
