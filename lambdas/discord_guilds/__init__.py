import json
import logging
import requests

from shared import middleware

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger, admin_check=False)
def handler(event, context):
    # get authorization header
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    if token is None:
        logger.info(
            json.dumps(
                {
                    "type": "MISSING_TOKEN",
                }
            )
        )
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "token is required"}),
        }

    res = requests.get(
        "https://discord.com/api/users/@me/guilds",
        headers={
            "Authorization": token
        }
    )

    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "INVALID_TOKEN",
                    "status_code": res.status_code,
                    "response": res.text
                }
            )
        )
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "token is invalid"}),
        }

    data = res.json()

    # 관리자권한을 가진 서버만 필터링합니다.
    guilds = [
        guild
        for guild in data
        if (guild["permissions"] & 0x8) == 0x8
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(guilds)
    }
