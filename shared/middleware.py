import json
import logging
import traceback

from shared.discord.utils import is_admin
from shared.exceptions import (
    BadRequestError,
    BaseException,
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

                    guild_id = (event.get("pathParameters", {}) or {}).get(
                        "guild_id", None
                    ) or (json.loads(event.get("body", "{}")) or {}).get(
                        "guild_id", None
                    )

                    if guild_id is None:
                        logger.info(json.dumps({"type": "MISSING_GUILD_ID"}))
                        raise BadRequestError()

                    is_admin_result, res = is_admin(guild_id, token)

                    if is_admin_result is False:
                        if res.status_code == 429:
                            logger.info(
                                json.dumps(
                                    {
                                        "type": "RATE_LIMITED",
                                        "guild_id": guild_id,
                                        "status_code": res.status_code,
                                        "response": res.text,
                                    }
                                )
                            )
                            raise RateLimitError(
                                retry_after=res.json().get("retry_after", 0)
                            )
                        else:
                            logger.info(
                                json.dumps(
                                    {
                                        "type": "NOT_ADMIN",
                                        "guild_id": guild_id,
                                        "status_code": res.status_code
                                        if res is not None
                                        else None,
                                        "response": res.text
                                        if res is not None
                                        else None,
                                    }
                                )
                            )
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
