import json
import logging
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Timeout
from urllib3.util.retry import Retry

from shared import middleware
from shared.discord import CHANNEL_TYPE
from shared.exceptions import (
    BotNotJoinedError,
    DiscordApiError,
    ServerNotFoundError,
    UnauthorizedError,
)
from shared.utils import build_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    raise_on_status=False,
)
adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
session.mount("https://", adapter)
session.headers.update({"Authorization": f"Bot {DISCORD_TOKEN}"})


@middleware(logger, admin_check=True)
def handler(event, context):
    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    try:
        res = session.get(
            f"https://discord.com/api/v10/guilds/{guild_id}/channels",
            timeout=Timeout(connect=3.05, read=5.0),
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_CONNECTION_FAILURE",
                    "guild_id": guild_id,
                    "error": str(e),
                }
            )
        )
        raise DiscordApiError(None)

    logger.info(
        json.dumps(
            {
                "type": "GET_GUILD_CHANNELS",
                "guild_id": guild_id,
                "status_code": res.status_code,
                "response": res.text,
            }
        )
    )

    if res.status_code == 404:
        raise ServerNotFoundError()

    if res.status_code == 403:
        raise BotNotJoinedError()

    if res.status_code == 401:
        raise UnauthorizedError()

    if res.status_code != 200:
        raise DiscordApiError(res)

    data = res.json()
    channels = [
        channel
        for channel in data
        if channel["type"] in [CHANNEL_TYPE.GUILD_TEXT, CHANNEL_TYPE.GUILD_NEWS]
    ]

    return build_response(200, data=channels)
