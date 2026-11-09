import json
import logging
import traceback

from shared.discord.utils import is_guild_admin
from shared.event import get_guild_id, get_token
from shared.exceptions import (
    BadRequestError,
    BaseException,
    UnauthorizedError,
    UserNotAdminError,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JSON_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def check_guild_admin(event: dict) -> None:
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
    try:
        is_admin = is_guild_admin(guild_id, token)
    except BaseException as e:
        logger.info(
            json.dumps(
                {"type": "ADMIN_CHECK_FAILED", "guild_id": guild_id, "code": e.code}
            )
        )
        raise

    if not is_admin:
        logger.info(json.dumps({"type": "NOT_ADMIN", "guild_id": guild_id}))
        raise UserNotAdminError()


def with_json_headers(res: dict | None) -> dict:
    res = res or {}
    return {**res, "headers": {**res.get("headers", {}), **JSON_HEADERS}}


def middleware(require_guild_admin: bool = False):
    def outer(func):
        def inner(event, context):
            logger.info(json.dumps(event))

            try:
                if require_guild_admin:
                    check_guild_admin(event)
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
