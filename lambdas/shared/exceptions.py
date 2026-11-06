import json
import math

from requests import Response


class BaseException(Exception):
    def __init__(
        self, status_code: int, code: str, message: str, details: dict | None = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self):
        return {
            "statusCode": self.status_code,
            "body": json.dumps(
                {
                    "code": self.code,
                    "message": self.message,
                    **self.details,
                }
            ),
        }


class BadRequestError(BaseException):
    def __init__(
        self,
        message="잘못된 요청입니다.",
        code="INVALID_REQUEST",
        details: dict | None = None,
    ):
        super().__init__(400, code, message, details)


class UnauthorizedError(BaseException):
    def __init__(self, message="로그인이 필요합니다. 다시 로그인해 주세요."):
        super().__init__(401, "UNAUTHORIZED", message)


class UserNotAdminError(BaseException):
    def __init__(self):
        super().__init__(403, "USER_NOT_ADMIN", "관리자 권한이 필요합니다.")


class BotForbiddenError(BaseException):
    def __init__(self):
        super().__init__(403, "BOT_FORBIDDEN", "봇이 해당 서버에 접근할 수 없습니다.")


class BotNotJoinedError(BaseException):
    def __init__(self):
        super().__init__(404, "BOT_NOT_JOINED", "봇이 서버에 초대되지 않았습니다.")


class ServerNotFoundError(BaseException):
    def __init__(self):
        super().__init__(404, "SERVER_NOT_FOUND", "서버를 찾을 수 없습니다.")


class DiscordChannelNotFoundError(BaseException):
    def __init__(self):
        super().__init__(
            404,
            "DISCORD_CHANNEL_NOT_FOUND",
            "디스코드 채널을 찾을 수 없습니다. 채널이 삭제되었는지 확인해 주세요.",
        )


class NotificationNotFoundError(BaseException):
    def __init__(self):
        super().__init__(
            404,
            "NOTIFICATION_NOT_FOUND",
            "알림을 찾을 수 없습니다. 새로고침 후 다시 시도해 주세요.",
        )


class ChzzkChannelNotFoundError(BaseException):
    def __init__(
        self, message="치지직 채널을 찾지 못했습니다. 채널 ID를 확인해 주세요."
    ):
        super().__init__(400, "CHZZK_CHANNEL_NOT_FOUND", message)


class ChzzkChannelUnavailableError(BaseException):
    def __init__(
        self,
        message="치지직에서 채널 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.",
    ):
        super().__init__(502, "CHZZK_CHANNEL_UNAVAILABLE", message)


class ChzzkChannelRegisterError(BaseException):
    def __init__(self):
        super().__init__(
            500,
            "CHZZK_CHANNEL_REGISTER_FAILED",
            "치지직 채널 정보를 저장하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        )


class ServiceFollowLimitError(BaseException):
    def __init__(self, account_index: int):
        super().__init__(
            503,
            "SERVICE_FOLLOW_LIMIT_REACHED",
            "서비스 계정의 팔로우 한도가 가득 찼습니다. "
            f"서포트 서버로 문의해 주세요. ({account_index})",
            {"account_index": account_index},
        )


class ServiceAccountBlockedError(BaseException):
    def __init__(self, account_index: int):
        super().__init__(
            403,
            "SERVICE_ACCOUNT_BLOCKED",
            "서비스 계정이 이 치지직 채널에서 차단되었습니다. "
            f"스트리머에게 차단 해제를 요청해 주세요. ({account_index})",
            {"account_index": account_index},
        )


class SendTestNotificationError(BaseException):
    def __init__(self, *, via_webhook=False, discord_message: str | None = None):
        message = (
            "커스텀 웹훅으로 테스트 알림을 보내지 못했습니다. 웹훅 URL을 확인해 주세요."
            if via_webhook
            else "테스트 알림을 보내지 못했습니다. 치직 봇의 채널 권한을 확인해 주세요."
        )
        super().__init__(
            500,
            "TEST_NOTIFICATION_WEBHOOK_FAILED"
            if via_webhook
            else "TEST_NOTIFICATION_FAILED",
            message,
            {"discord_message": discord_message} if discord_message else None,
        )


class RateLimitError(BaseException):
    def __init__(self, retry_after=0):
        self.retry_after = retry_after
        super().__init__(
            429,
            "RATE_LIMITED",
            "디스코드에 요청이 몰려 일시적으로 제한되었습니다. "
            f"{self._wait_text(retry_after)} 뒤 다시 시도해 주세요.",
        )

    @staticmethod
    def _wait_text(retry_after) -> str:
        if not retry_after or retry_after <= 0:
            return "잠시"
        seconds = math.ceil(retry_after)
        if seconds >= 60:
            return f"약 {math.ceil(seconds / 60)}분"
        return f"약 {seconds}초"

    def to_dict(self):
        return {
            "statusCode": self.status_code,
            "body": json.dumps(
                {
                    "code": self.code,
                    "message": self.message,
                    "retry_after": self.retry_after,
                }
            ),
        }


class DiscordApiUnavailableError(BaseException):
    """응답 객체 없이 디스코드 API 호출이 실패했을 때(Timeout, 연결 실패, 5xx 등) 사용합니다."""

    def __init__(
        self,
        message="디스코드와 연결이 원활하지 않습니다. 잠시 뒤 다시 시도해 주세요.",
    ):
        super().__init__(502, "DISCORD_API_ERROR", message)


class DiscordApiError(BaseException):
    def __init__(self, res: Response, message="디스코드 API 통신 중 오류 발생"):
        super().__init__(
            502,
            "DISCORD_API_ERROR",
            f"{message} (Status: {res.status_code}, Response: {res.text})",
        )
