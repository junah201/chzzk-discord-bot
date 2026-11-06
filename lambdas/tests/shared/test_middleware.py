import importlib
import json
import logging

import pytest
from shared import middleware
from shared.discord.utils import AdminCheckResult
from shared.exceptions import BadRequestError, UserNotAdminError

# `shared/__init__.py`가 `middleware` 함수를 같은 이름으로 re-export 하므로
# `shared.middleware` 문자열 경로로는 함수가 잡힌다. patch 대상은 모듈 객체로 가져온다.
middleware_module = importlib.import_module("shared.middleware")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


@pytest.fixture
def logger():
    return logging.getLogger("test_middleware")


@pytest.fixture
def handler(mocker):
    return mocker.Mock(return_value={"statusCode": 200, "body": "{}"})


@pytest.fixture
def is_admin(mocker):
    return mocker.patch.object(
        middleware_module, "is_admin", return_value=AdminCheckResult(True, 200)
    )


def admin_event(**overrides):
    event = {
        "headers": {"Authorization": "Bearer token"},
        "pathParameters": {"guild_id": "123"},
    }
    event.update(overrides)
    return event


class TestResponseHandling:
    def test_adds_cors_and_json_headers(self, logger, handler):
        res = middleware(logger)(handler)({}, None)

        assert res == {"statusCode": 200, "body": "{}", "headers": CORS_HEADERS}

    def test_passes_event_and_context_to_handler(self, logger, handler):
        event, context = {"a": 1}, object()
        middleware(logger)(handler)(event, context)

        handler.assert_called_once_with(event, context)

    def test_keeps_existing_headers_but_overrides_content_type(self, logger, handler):
        handler.return_value = {
            "statusCode": 200,
            "headers": {"X-Custom": "1", "Content-Type": "text/plain"},
        }

        res = middleware(logger)(handler)({}, None)

        assert res["headers"] == {"X-Custom": "1", **CORS_HEADERS}

    def test_none_response_has_only_headers(self, logger, handler):
        # 현재 동작: 핸들러가 None을 반환하면 statusCode 없이 headers만 반환된다.
        handler.return_value = None

        assert middleware(logger)(handler)({}, None) == {"headers": CORS_HEADERS}

    def test_default_logger_is_used_when_not_given(self, handler):
        res = middleware()(handler)({}, None)

        assert res["statusCode"] == 200

    def test_logs_event(self, mocker, logger, handler):
        info = mocker.patch.object(logger, "info")

        middleware(logger)(handler)({"path": "/x"}, None)

        info.assert_called_once_with(json.dumps({"path": "/x"}))


class TestExceptionHandling:
    def test_base_exception_becomes_error_response(self, logger, handler):
        handler.side_effect = BadRequestError("잘못됨")

        res = middleware(logger)(handler)({}, None)

        assert res["statusCode"] == 400
        assert json.loads(res["body"]) == {
            "code": "INVALID_REQUEST",
            "message": "잘못됨",
        }
        assert res["headers"] == CORS_HEADERS

    def test_base_exception_is_not_logged_as_error(self, mocker, logger, handler):
        error = mocker.patch.object(logger, "error")
        handler.side_effect = UserNotAdminError()

        middleware(logger)(handler)({}, None)

        error.assert_not_called()

    def test_unexpected_exception_becomes_500(self, mocker, logger, handler):
        error = mocker.patch.object(logger, "error")
        handler.side_effect = ValueError("터짐")

        res = middleware(logger)(handler)({}, None)

        assert res["statusCode"] == 500
        assert json.loads(res["body"]) == "터짐"
        assert res["headers"] == CORS_HEADERS
        error.assert_called_once()
        logged = json.loads(error.call_args.args[0])
        assert logged["error"] == "터짐"
        assert "ValueError" in logged["traceback"]


class TestAdminCheck:
    def wrap(self, logger, handler):
        return middleware(logger, admin_check=True)(handler)

    def test_admin_calls_handler(self, logger, handler, is_admin):
        event = admin_event()

        res = self.wrap(logger, handler)(event, None)

        assert res["statusCode"] == 200
        is_admin.assert_called_once_with("123", "Bearer token")
        handler.assert_called_once_with(event, None)

    @pytest.mark.parametrize(
        "headers",
        [{}, {"authorization": "Bearer token"}],
        ids=["missing", "lowercase-key"],
    )
    def test_missing_token_is_401(self, logger, handler, is_admin, headers):
        # 현재 동작: 헤더 키는 대소문자를 구분해서 `Authorization`만 인식한다.
        res = self.wrap(logger, handler)(admin_event(headers=headers), None)

        assert res["statusCode"] == 401
        assert json.loads(res["body"])["code"] == "UNAUTHORIZED"
        is_admin.assert_not_called()
        handler.assert_not_called()

    def test_event_without_headers_is_401(self, logger, handler, is_admin):
        res = self.wrap(logger, handler)({}, None)

        assert res["statusCode"] == 401
        is_admin.assert_not_called()

    def test_guild_id_from_body(self, logger, handler, is_admin):
        event = admin_event(pathParameters=None, body=json.dumps({"guild_id": "456"}))

        res = self.wrap(logger, handler)(event, None)

        assert res["statusCode"] == 200
        is_admin.assert_called_once_with("456", "Bearer token")

    def test_path_guild_id_takes_precedence_over_body(self, logger, handler, is_admin):
        event = admin_event(body=json.dumps({"guild_id": "456"}))

        self.wrap(logger, handler)(event, None)

        is_admin.assert_called_once_with("123", "Bearer token")

    @pytest.mark.parametrize(
        "overrides",
        [
            {"pathParameters": None},
            {"pathParameters": {}},
            {"pathParameters": None, "body": "{}"},
            {"pathParameters": None, "body": "null"},
            {"pathParameters": {"guild_id": None}, "body": json.dumps({"x": 1})},
            {"pathParameters": None, "body": None},
            {"pathParameters": None, "body": ""},
            {"pathParameters": None, "body": "not-json"},
            {"pathParameters": None, "body": "[1, 2]"},
            {"pathParameters": None, "body": '"123"'},
        ],
        ids=[
            "no-path-no-body",
            "empty-path",
            "empty-body",
            "null-json-body",
            "no-guild-in-either",
            "body-none",
            "body-empty-string",
            "invalid-json",
            "json-array",
            "json-string",
        ],
    )
    def test_missing_guild_id_is_400(self, logger, handler, is_admin, overrides):
        res = self.wrap(logger, handler)(admin_event(**overrides), None)

        assert res["statusCode"] == 400
        assert json.loads(res["body"])["code"] == "INVALID_REQUEST"
        is_admin.assert_not_called()
        handler.assert_not_called()

    def test_body_is_not_parsed_when_path_has_guild_id(self, logger, handler, is_admin):
        res = self.wrap(logger, handler)(admin_event(body="not-json"), None)

        assert res["statusCode"] == 200
        is_admin.assert_called_once_with("123", "Bearer token")

    def test_rate_limited_is_429_with_retry_after(self, logger, handler, is_admin):
        is_admin.return_value = AdminCheckResult(
            False, 429, "RateLimited: {}", retry_after=2.5
        )

        res = self.wrap(logger, handler)(admin_event(), None)

        assert res["statusCode"] == 429
        assert json.loads(res["body"]) == {
            "code": "RATE_LIMITED",
            "message": "디스코드에 요청이 몰려 일시적으로 제한되었습니다. 약 3초 뒤 다시 시도해 주세요.",
            "retry_after": 2.5,
        }
        assert res["headers"] == CORS_HEADERS
        handler.assert_not_called()

    def test_rate_limited_without_retry_after_defaults_to_zero(
        self, logger, handler, is_admin
    ):
        is_admin.return_value = AdminCheckResult(False, 429, "RateLimited: {}")

        res = self.wrap(logger, handler)(admin_event(), None)

        assert json.loads(res["body"])["retry_after"] == 0

    @pytest.mark.parametrize(
        "status_code", [200, 401, 403, 404], ids=["not-admin", "401", "403", "404"]
    )
    def test_not_admin_is_403(self, logger, handler, is_admin, status_code):
        is_admin.return_value = AdminCheckResult(False, status_code, "")

        res = self.wrap(logger, handler)(admin_event(), None)

        assert res["statusCode"] == 403
        assert json.loads(res["body"])["code"] == "USER_NOT_ADMIN"
        handler.assert_not_called()

    @pytest.mark.parametrize(
        "status_code",
        [-1, -2, -3, 500, 503],
        ids=["timeout", "connection-error", "unknown-error", "500", "503"],
    )
    def test_discord_failure_is_502(self, logger, handler, is_admin, status_code):
        is_admin.return_value = AdminCheckResult(False, status_code, "error")

        res = self.wrap(logger, handler)(admin_event(), None)

        assert res["statusCode"] == 502
        assert json.loads(res["body"])["code"] == "DISCORD_API_ERROR"
        assert res["headers"] == CORS_HEADERS
        handler.assert_not_called()

    def test_admin_check_disabled_skips_is_admin(self, logger, handler, is_admin):
        res = middleware(logger)(handler)({}, None)

        assert res["statusCode"] == 200
        is_admin.assert_not_called()
