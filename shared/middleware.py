import json
import logging
import traceback

from shared.discord.utils import is_admin


def middleware(logger: logging.Logger | None = None, admin_check: bool = False):
    if logger is None:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    def outer(func):
        def inner(event, context):
            logger.info(json.dumps(event))

            if admin_check:
                headers = event.get("headers", {})
                token = headers.get("Authorization", None)

                if token is None:
                    logger.info(json.dumps({"type": "MISSING_TOKEN"}))
                    return {
                        "statusCode": 401,
                        "body": json.dumps({"message": "token is required"}),
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                        },
                    }

                guild_id = (event.get("pathParameters", {}) or {}).get(
                    "guild_id", None
                ) or (json.loads(event.get("body", "{}")) or {}).get("guild_id", None)

                if guild_id is None:
                    logger.info(json.dumps({"type": "MISSING_GUILD_ID"}))
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"message": "guild_id is required"}),
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*",
                        },
                    }

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
                        return {
                            "statusCode": 429,
                            "body": json.dumps(
                                {
                                    **res.json(),
                                    "message": "너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요.",
                                }
                            ),
                            "headers": {
                                "Content-Type": "application/json",
                                "Access-Control-Allow-Origin": "*",
                            },
                        }
                    else:
                        logger.info(
                            json.dumps(
                                {
                                    "type": "NOT_ADMIN",
                                    "guild_id": guild_id,
                                    "status_code": res.status_code
                                    if res is not None
                                    else None,
                                    "response": res.text if res is not None else None,
                                }
                            )
                        )
                        return {
                            "statusCode": 400,
                            "body": json.dumps(
                                {"message": "해당 서버에 대한 관리자 권한이 없습니다."}
                            ),
                            "headers": {
                                "Content-Type": "application/json",
                                "Access-Control-Allow-Origin": "*",
                            },
                        }

            try:
                res = func(event, context)
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
