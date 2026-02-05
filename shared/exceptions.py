import json

from requests import Response


class BaseException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)

    def to_dict(self):
        return {
            "statusCode": self.status_code,
            "body": json.dumps(
                {
                    "code": self.code,
                    "message": self.message,
                }
            ),
        }


class BadRequestError(BaseException):
    def __init__(self, message="잘못된 요청입니다."):
        super().__init__(400, "INVALID_REQUEST", message)


class UnauthorizedError(BaseException):
    def __init__(self, message="로그인이 필요합니다."):
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


class RateLimitError(BaseException):
    def __init__(self, retry_after=0):
        self.retry_after = retry_after
        super().__init__(429, "RATE_LIMITED", "요청이 너무 많습니다.")

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


class DiscordApiError(BaseException):
    def __init__(self, res: Response, message="디스코드 API 통신 중 오류 발생"):
        super().__init__(
            502,
            "DISCORD_API_ERROR",
            f"{message} (Status: {res.status_code}, Response: {res.text})",
        )
