import json
import logging
import requests

from shared import middleware


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
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
        "https://discord.com/api/users/@me",
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

    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }
