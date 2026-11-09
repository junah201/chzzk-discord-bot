import json
import logging

import requests
from shared import middleware
from shared.discord.utils import DISCORD_API_BASE_URL, DISCORD_API_TIMEOUT_SEC
from shared.event import get_token
from shared.exceptions import UnauthorizedError
from shared.utils import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware()
def handler(event, _context):
    token = get_token(event)

    if token is None:
        logger.info(json.dumps({"type": "MISSING_TOKEN"}))
        raise UnauthorizedError()

    res = requests.get(
        f"{DISCORD_API_BASE_URL}/users/@me",
        headers={"Authorization": token},
        timeout=DISCORD_API_TIMEOUT_SEC,
    )

    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "INVALID_TOKEN",
                    "status_code": res.status_code,
                    "response": res.text,
                }
            )
        )
        raise UnauthorizedError()

    data = res.json()
    logger.info(
        json.dumps(
            {"type": "GET_USER", "status_code": res.status_code, "response": data},
            ensure_ascii=False,
        )
    )

    return build_response(200, data=data)
