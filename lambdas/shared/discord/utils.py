import json
import logging
import os
import time
from typing import NamedTuple

import requests

from .dataclass import PartialGuild

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_USER_GUILDS_URL = "https://discord.com/api/users/@me/guilds"
DISCORD_API_TIMEOUT_SEC = 3
# Lambda 기본 timeout(10초) 안에서 끝나도록 rate limit 대기 시간을 제한한다.
MAX_RATE_LIMIT_WAIT_SEC = 3
ADMINISTRATOR_PERMISSION = 0x8

logger = logging.getLogger()


def delete_message(channel_id: int, message_id: int):
    res = requests.delete(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
    )
    if res.status_code != 204:
        raise Exception(f"Failed to delete message: {res.status_code} {res.text}")


def send_message(
    channel_id: int, data: dict, files: dict | None = None, token=DISCORD_TOKEN
):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}
    if files:
        form_data = {}
        if data:
            form_data["payload_json"] = json.dumps(data)

        res = requests.post(url, headers=headers, data=form_data, files=files)
    else:
        headers["Content-Type"] = "application/json"
        res = requests.post(url, headers=headers, data=json.dumps(data))

    return res


def get_channel(channel_id, token=DISCORD_TOKEN) -> dict | None:
    res = requests.get(
        f"https://discord.com/api/v10/channels/{channel_id}",
        headers={
            "Authorization": f"Bot {token}",
        },
    )
    if res.status_code != 200:
        return None

    return res.json()


class AdminCheckResult(NamedTuple):
    is_admin: bool
    status_code: int
    error_message: str = ""
    retry_after: float = 0


def is_admin(guild_id: str, token: str = None, retry: int = 3) -> AdminCheckResult:
    """
    해당 유저가 관리자 권한을 가진 서버인지 확인합니다.
    관리자면 (True, 200, "", 0.0), 관리자가 아니면 (False, 200, "", 0.0)를 반환하고,
    실패 시 (False, status_code, error_message, retry_after)를 반환합니다.
    status_code는 HTTP 상태 코드이며, Timeout은 -1, ConnectionError는 -2, 알 수 없는 오류나 잘못된 응답은 -3입니다.
    rate limit(429)으로 실패하면 retry_after에 대기해야 할 시간(초)이 담깁니다.
    """
    retry = max(1, retry)

    for attempt in range(1, retry + 1):
        try:
            res = requests.get(
                DISCORD_USER_GUILDS_URL,
                headers={"Authorization": token},
                timeout=DISCORD_API_TIMEOUT_SEC,
            )
        except requests.exceptions.Timeout as e:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_IS_ADMIN_TIMEOUT",
                        "guild_id": guild_id,
                        "exception": str(e),
                    }
                )
            )
            return AdminCheckResult(False, -1, f"TimeoutError: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_IS_ADMIN_CONNECTION_ERROR",
                        "guild_id": guild_id,
                        "exception": str(e),
                    }
                )
            )
            return AdminCheckResult(False, -2, f"ConnectionError: {str(e)}")
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_IS_ADMIN_UNKNOWN_ERROR",
                        "guild_id": guild_id,
                        "exception": str(e),
                    }
                )
            )
            return AdminCheckResult(False, -3, f"UnknownError: {str(e)}")

        if res.status_code == 429:
            try:
                retry_after = float(res.json()["retry_after"])
            except Exception:
                retry_after = 0
            if attempt < retry and retry_after <= MAX_RATE_LIMIT_WAIT_SEC:
                time.sleep(retry_after + 0.1)
                continue

            logger.warning(
                json.dumps(
                    {
                        "type": "DISCORD_IS_ADMIN_RATE_LIMITED",
                        "guild_id": guild_id,
                        "attempt": attempt,
                        "retry_after": retry_after,
                    }
                )
            )
            return AdminCheckResult(False, 429, f"RateLimited: {res.text}", retry_after)

        if res.status_code != 200:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_IS_ADMIN_HTTP_ERROR",
                        "guild_id": guild_id,
                        "status_code": res.status_code,
                        "text": res.text,
                    }
                )
            )
            return AdminCheckResult(
                False, res.status_code, f"HTTPError: {res.status_code} - {res.text}"
            )

        break

    # 관리자 권한을 가진 서버만 필터링합니다.
    try:
        guilds: list[PartialGuild] = res.json()
        admin_guild_ids = {
            guild["id"]
            for guild in guilds
            if guild["permissions"] & ADMINISTRATOR_PERMISSION
            == ADMINISTRATOR_PERMISSION
        }
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_IS_ADMIN_INVALID_RESPONSE",
                    "guild_id": guild_id,
                    "exception": str(e),
                    "text": res.text[:1000],
                }
            )
        )
        return AdminCheckResult(False, -3, f"InvalidResponse: {str(e)}")

    return AdminCheckResult(guild_id in admin_guild_ids, 200, "")
