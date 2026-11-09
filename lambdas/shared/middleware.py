import json
import logging
import traceback

from shared.discord.utils import AdminCheckResult, is_admin
from shared.event import get_guild_id, get_token
from shared.exceptions import (
    BadRequestError,
    BaseException,
    DiscordApiUnavailableError,
    RateLimitError,
    UnauthorizedError,
    UserNotAdminError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JSON_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def admin_check_error(
    result: AdminCheckResult,
) -> tuple[str, BaseException] | None:
    """관리자면 None을, 아니면 (로그 type, 응답으로 보낼 예외)를 반환한다."""
    if result.is_admin:
        return None
    if result.status_code == 429:
        return "RATE_LIMITED", RateLimitError(retry_after=result.retry_after)
    # Timeout/연결 실패(음수) 또는 디스코드 서버 오류(5xx)는 권한 문제가 아니다.
    if result.status_code < 0 or result.status_code >= 500:
        return "DISCORD_API_UNAVAILABLE", DiscordApiUnavailableError()
    return "NOT_ADMIN", UserNotAdminError()


def check_admin(event: dict) -> None:
    token = get_token(event)
    if token is None:
        logger.info(json.dumps({"type": "MISSING_TOKEN"}))
        raise UnauthorizedError()

    try:
        guild_id = get_guild_id(event)
    except BadRequestError:
        logger.info(json.dumps({"type": "INVALID_JSON_BODY"}))
        raise
    if guild_id is None:
        logger.info(json.dumps({"type": "MISSING_GUILD_ID"}))
        raise BadRequestError()

    # 따로 rate limit을 두지 않은 이유: token은 요청한 유저의 OAuth 토큰이다.
    # 디스코드는 토큰별로 rate limit을 걸기 때문에 요청을 반복한 유저만
    # 429를 받고, 다른 유저는 영향을 받지 않는다.
    result = is_admin(guild_id, token)

    error = admin_check_error(result)
    if error is None:
        return

    log_type, exception = error
    logger.info(
        json.dumps(
            {
                "type": log_type,
                "guild_id": guild_id,
                "status_code": result.status_code,
                "error_message": result.error_message,
            }
        )
    )
    raise exception


def with_json_headers(res: dict | None) -> dict:
    res = res or {}
    return {**res, "headers": {**res.get("headers", {}), **JSON_HEADERS}}


def middleware(require_guild_admin: bool = False):
    def outer(func):
        def inner(event, context):
            logger.info(json.dumps(event))

            try:
                if require_guild_admin:
                    check_admin(event)
                res = func(event, context)
            except BaseException as e:
                res = e.to_dict()
            except Exception as e:
                logger.error(
                    json.dumps(
                        {"error": str(e), "traceback": traceback.format_exc()},
                        ensure_ascii=False,
                    )
                )
                res = {
                    "statusCode": 500,
                    "body": json.dumps(str(e), ensure_ascii=False),
                }

            return with_json_headers(res)

        return inner

    return outer
