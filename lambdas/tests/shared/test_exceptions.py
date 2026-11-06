import json

import pytest
from shared.exceptions import (
    BadRequestError,
    BaseException,
    BotForbiddenError,
    BotNotJoinedError,
    DiscordApiError,
    DiscordApiUnavailableError,
    RateLimitError,
    ServerNotFoundError,
    UnauthorizedError,
    UserNotAdminError,
)


@pytest.mark.parametrize(
    ("error", "status_code", "code", "message"),
    [
        (BadRequestError(), 400, "INVALID_REQUEST", "잘못된 요청입니다."),
        (
            UnauthorizedError(),
            401,
            "UNAUTHORIZED",
            "로그인이 필요합니다. 다시 로그인해 주세요.",
        ),
        (UserNotAdminError(), 403, "USER_NOT_ADMIN", "관리자 권한이 필요합니다."),
        (
            BotForbiddenError(),
            403,
            "BOT_FORBIDDEN",
            "봇이 해당 서버에 접근할 수 없습니다.",
        ),
        (
            BotNotJoinedError(),
            404,
            "BOT_NOT_JOINED",
            "봇이 서버에 초대되지 않았습니다.",
        ),
        (ServerNotFoundError(), 404, "SERVER_NOT_FOUND", "서버를 찾을 수 없습니다."),
        (
            RateLimitError(),
            429,
            "RATE_LIMITED",
            "디스코드에 요청이 몰려 일시적으로 제한되었습니다. 잠시 뒤 다시 시도해 주세요.",
        ),
        (
            DiscordApiUnavailableError(),
            502,
            "DISCORD_API_ERROR",
            "디스코드와 연결이 원활하지 않습니다. 잠시 뒤 다시 시도해 주세요.",
        ),
    ],
    ids=lambda v: v.__class__.__name__ if isinstance(v, Exception) else None,
)
def test_to_dict(error, status_code, code, message):
    res = error.to_dict()
    body = json.loads(res["body"])

    assert res["statusCode"] == status_code
    assert body["code"] == code
    assert body["message"] == message
    assert isinstance(error, BaseException)
    assert str(error) == message


@pytest.mark.parametrize(
    "error_cls", [BadRequestError, UnauthorizedError, DiscordApiUnavailableError]
)
def test_custom_message(error_cls):
    error = error_cls("커스텀 메시지")
    assert json.loads(error.to_dict()["body"])["message"] == "커스텀 메시지"


def test_bad_request_with_code_and_details():
    error = BadRequestError("메시지", code="SOME_CODE", details={"max_limit": 5})

    assert json.loads(error.to_dict()["body"]) == {
        "code": "SOME_CODE",
        "message": "메시지",
        "max_limit": 5,
    }


def test_base_exception_is_a_builtin_exception():
    # middleware가 `except BaseException` 다음 `except Exception`으로 처리하므로 Exception 하위여야 한다.
    assert issubclass(BaseException, Exception)


class TestRateLimitError:
    def test_default_retry_after_is_zero(self):
        body = json.loads(RateLimitError().to_dict()["body"])
        assert body["retry_after"] == 0

    def test_includes_retry_after(self):
        error = RateLimitError(retry_after=1.5)
        body = json.loads(error.to_dict()["body"])

        assert error.retry_after == 1.5
        assert body == {
            "code": "RATE_LIMITED",
            "message": "디스코드에 요청이 몰려 일시적으로 제한되었습니다. 약 2초 뒤 다시 시도해 주세요.",
            "retry_after": 1.5,
        }

    @pytest.mark.parametrize(
        ("retry_after", "wait"),
        [
            (0, "잠시"),
            (-1, "잠시"),
            (0.2, "약 1초"),
            (59, "약 59초"),
            (59.5, "약 1분"),
            (60, "약 1분"),
            (61, "약 2분"),
        ],
    )
    def test_message_shows_wait_time(self, retry_after, wait):
        assert RateLimitError(retry_after).message == (
            f"디스코드에 요청이 몰려 일시적으로 제한되었습니다. {wait} 뒤 다시 시도해 주세요."
        )


class TestDiscordApiError:
    def test_message_includes_status_and_response(self, mocker):
        res = mocker.Mock(status_code=500, text="boom")
        error = DiscordApiError(res)

        assert error.status_code == 502
        assert error.code == "DISCORD_API_ERROR"
        assert (
            error.message
            == "디스코드 API 통신 중 오류 발생 (Status: 500, Response: boom)"
        )

    def test_custom_message_prefix(self, mocker):
        res = mocker.Mock(status_code=403, text="Missing Access")
        error = DiscordApiError(res, message="채널 조회 실패")

        assert error.message == "채널 조회 실패 (Status: 403, Response: Missing Access)"
