import json
import logging
import os
import time
from typing import NamedTuple

import requests

from .dataclass import PartialGuild

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
# 디스코드 API는 v10으로 고정한다. 버전 없는 경로는 deprecated된 v6 형식으로 응답한다.
DISCORD_API_BASE_URL = "https://discord.com/api/v10"
DISCORD_USER_GUILDS_URL = f"{DISCORD_API_BASE_URL}/users/@me/guilds"
DISCORD_API_TIMEOUT_SEC = 3
# Lambda 기본 timeout(10초) 안에서 끝나도록 rate limit 대기 시간을 제한한다.
MAX_RATE_LIMIT_WAIT_SEC = 3
ADMINISTRATOR_PERMISSION = 0x8

logger = logging.getLogger()


def delete_message(channel_id: int, message_id: int):
    res = requests.delete(
        f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages/{message_id}",
        headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
    )
    if res.status_code != 204:
        raise Exception(f"Failed to delete message: {res.status_code} {res.text}")


def send_message(
    channel_id: int, data: dict, files: dict | None = None, token=DISCORD_TOKEN
):
    url = f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages"
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
        f"{DISCORD_API_BASE_URL}/channels/{channel_id}",
        headers={
            "Authorization": f"Bot {token}",
        },
    )
    if res.status_code != 200:
        return None

    return res.json()


class AdminGuildsResult(NamedTuple):
    guilds: list[PartialGuild] | None
    status_code: int
    error_message: str = ""
    retry_after: float = 0


class AdminCheckResult(NamedTuple):
    is_admin: bool
    status_code: int
    error_message: str = ""
    retry_after: float = 0


def get_admin_guilds(
    token: str, with_counts: bool = False, retry: int = 3
) -> AdminGuildsResult:
    """유저가 관리자 권한을 가진 서버 목록을 가져옵니다.
    성공 시 (guilds, 200, "")를 반환하고, 실패 시 (None, status_code, error_message, retry_after)를 반환합니다.
    status_code는 HTTP 상태 코드이며, Timeout은 -1, ConnectionError는 -2, 알 수 없는 오류나 잘못된 응답은 -3입니다.
    rate limit(429)으로 실패하면 retry_after에 대기해야 할 시간(초)이 담깁니다.
    with_counts가 True면 approximate_member_count/approximate_presence_count가 포함됩니다.
    """
    retry = max(1, retry)
    params = {"with_counts": "true"} if with_counts else None

    for attempt in range(1, retry + 1):
        try:
            res = requests.get(
                DISCORD_USER_GUILDS_URL,
                headers={"Authorization": token},
                params=params,
                timeout=DISCORD_API_TIMEOUT_SEC,
            )
        except requests.exceptions.Timeout as e:
            logger.error(
                json.dumps(
                    {"type": "DISCORD_GET_ADMIN_GUILDS_TIMEOUT", "exception": str(e)}
                )
            )
            return AdminGuildsResult(None, -1, f"TimeoutError: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_GET_ADMIN_GUILDS_CONNECTION_ERROR",
                        "exception": str(e),
                    }
                )
            )
            return AdminGuildsResult(None, -2, f"ConnectionError: {str(e)}")
        except Exception as e:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_GET_ADMIN_GUILDS_UNKNOWN_ERROR",
                        "exception": str(e),
                    }
                )
            )
            return AdminGuildsResult(None, -3, f"UnknownError: {str(e)}")

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
                        "type": "DISCORD_GET_ADMIN_GUILDS_RATE_LIMITED",
                        "attempt": attempt,
                        "retry_after": retry_after,
                    }
                )
            )
            return AdminGuildsResult(None, 429, f"RateLimited: {res.text}", retry_after)

        if res.status_code != 200:
            logger.error(
                json.dumps(
                    {
                        "type": "DISCORD_GET_ADMIN_GUILDS_HTTP_ERROR",
                        "status_code": res.status_code,
                        "text": res.text,
                    }
                )
            )
            return AdminGuildsResult(
                None, res.status_code, f"HTTPError: {res.status_code} - {res.text}"
            )

        break

    # 관리자 권한을 가진 서버만 필터링합니다. (v10의 permissions는 문자열이다.)
    try:
        guilds: list[PartialGuild] = res.json()
        admin_guilds = [
            guild
            for guild in guilds
            if int(guild["permissions"]) & ADMINISTRATOR_PERMISSION
            == ADMINISTRATOR_PERMISSION
        ]
        if any("id" not in guild for guild in admin_guilds):
            raise KeyError("id")
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_GET_ADMIN_GUILDS_INVALID_RESPONSE",
                    "exception": str(e),
                    "text": res.text[:1000],
                }
            )
        )
        return AdminGuildsResult(None, -3, f"InvalidResponse: {str(e)}")

    return AdminGuildsResult(admin_guilds, 200, "")


def is_admin(guild_id: str, token: str = None, retry: int = 3) -> AdminCheckResult:
    """
    해당 유저가 관리자 권한을 가진 서버인지 확인합니다.
    관리자면 (True, 200, "", 0.0), 관리자가 아니면 (False, 200, "", 0.0)를 반환하고,
    실패 시 (False, status_code, error_message, retry_after)를 반환합니다.
    status_code와 retry_after는 get_admin_guilds와 같습니다.
    """
    result = get_admin_guilds(token, retry=retry)
    if result.guilds is None:
        return AdminCheckResult(
            False, result.status_code, result.error_message, result.retry_after
        )

    return AdminCheckResult(
        any(guild["id"] == guild_id for guild in result.guilds), 200, ""
    )
