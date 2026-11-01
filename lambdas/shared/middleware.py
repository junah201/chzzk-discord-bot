import json
import logging
import traceback

from shared.discord.utils import is_admin
from shared.exceptions import (
    BadRequestError,
    BaseException,
    DiscordApiUnavailableError,
    RateLimitError,
    UnauthorizedError,
    UserNotAdminError,
)


def middleware(logger: logging.Logger | None = None, admin_check: bool = False):
    if logger is None:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    def outer(func):
        def inner(event, context):
            logger.info(json.dumps(event))

            try:
                if admin_check:
                    headers = event.get("headers", {})
                    token = headers.get("Authorization", None)

                    if token is None:
                        logger.info(json.dumps({"type": "MISSING_TOKEN"}))
                        raise UnauthorizedError()

                    guild_id = (event.get("pathParameters") or {}).get("guild_id")

                    if not guild_id:
                        # API Gateway는 body가 없으면 "body": null을 보낸다.
                        try:
                            body = json.loads(event.get("body") or "{}")
                        except json.JSONDecodeError as e:
                            logger.info(json.dumps({"type": "INVALID_JSON_BODY"}))
                            raise BadRequestError() from e
                        if isinstance(body, dict):
                            guild_id = body.get("guild_id")

                    if guild_id is None:
                        logger.info(json.dumps({"type": "MISSING_GUILD_ID"}))
                        raise BadRequestError()

                    result = is_admin(guild_id, token)

                    if not result.is_admin:
                        log_data = {
                            "guild_id": guild_id,
                            "status_code": result.status_code,
                            "error_message": result.error_message,
                        }
                        if result.status_code == 429:
                            logger.info(
                                json.dumps({"type": "RATE_LIMITED", **log_data})
                            )
                            raise RateLimitError(retry_after=result.retry_after)
                        # Timeout/연결 실패(음수) 또는 디스코드 서버 오류(5xx)는 권한 문제가 아니다.
                        if result.status_code < 0 or result.status_code >= 500:
                            logger.info(
                                json.dumps(
                                    {"type": "DISCORD_API_UNAVAILABLE", **log_data}
                                )
                            )
                            raise DiscordApiUnavailableError()
                        logger.info(json.dumps({"type": "NOT_ADMIN", **log_data}))
                        raise UserNotAdminError()

                res = func(event, context)
            except BaseException as e:
                return {
                    **e.to_dict(),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                }
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

            res = res or {}
            res["headers"] = res.get("headers", {})
            res["headers"]["Access-Control-Allow-Origin"] = "*"
            res["headers"]["Content-Type"] = "application/json"
            return res

        return inner

    return outer
