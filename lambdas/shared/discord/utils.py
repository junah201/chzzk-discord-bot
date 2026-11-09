import http.cookiejar
import json
import logging
import os
import time
from typing import NamedTuple

import requests

from shared.exceptions import (
    BaseException,
    DiscordApiUnavailableError,
    RateLimitError,
    UnauthorizedError,
)

from .dataclass import PartialGuild

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
# 디스코드 API는 v10으로 고정한다. 버전 없는 경로는 deprecated된 v6 형식으로 응답한다.
DISCORD_API_BASE_URL = "https://discord.com/api/v10"
DISCORD_USER_GUILDS_URL = f"{DISCORD_API_BASE_URL}/users/@me/guilds"
# (connect, read). 콜드 스타트 직후 첫 요청은 응답이 3초를 넘기기도 한다.
DISCORD_API_TIMEOUT_SEC = (3.05, 6)
# 메시지 전송은 파일 첨부가 있을 수 있어 조금 더 기다린다.
DISCORD_MESSAGE_TIMEOUT_SEC = 5
# 네트워크 오류로 응답을 받지 못했을 때 쓰는 상태 코드 (HTTP 표준 코드가 아니다).
NETWORK_ERROR_STATUS_CODE = 599
# Lambda 기본 timeout(10초) 안에서 끝나도록 rate limit 대기 시간을 제한한다.
MAX_RATE_LIMIT_WAIT_SEC = 3
ADMINISTRATOR_PERMISSION = 0x8

logger = logging.getLogger()


def _create_session() -> requests.Session:
    session = requests.Session()
    # 여러 토큰(봇, 유저 OAuth)의 요청이 세션을 같이 쓰므로 응답 쿠키를 다음 요청에 싣지 않는다.
    session.cookies.set_policy(http.cookiejar.DefaultCookiePolicy(allowed_domains=[]))
    return session


# 같은 Lambda 실행 환경 안에서 연결을 재사용해서 요청마다 TLS 핸드셰이크를 하지 않는다.
# 인증 헤더는 요청마다 넘긴다.
session = _create_session()


def network_error_response(error: Exception) -> requests.Response:
    """네트워크 오류를 상태 코드 599인 Response로 바꿉니다. 본문에는 오류 메시지가 담깁니다."""
    response = requests.Response()
    response.status_code = NETWORK_ERROR_STATUS_CODE
    response._content = str(error).encode()
    return response


def delete_message(channel_id: int, message_id: int):
    try:
        res = session.delete(
            f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages/{message_id}",
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
            timeout=DISCORD_API_TIMEOUT_SEC,
        )
    except requests.RequestException as e:
        raise Exception(f"Failed to delete message: {e}") from e
    if res.status_code != 204:
        raise Exception(f"Failed to delete message: {res.status_code} {res.text}")


def send_message(
    channel_id: int, data: dict, files: dict | None = None, token=DISCORD_TOKEN
) -> requests.Response:
    """채널에 메시지를 보냅니다. 네트워크 오류가 나면 예외 대신 상태 코드 599인 Response를 반환합니다."""
    url = f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {token}"}
    try:
        if files:
            form_data = {}
            if data:
                form_data["payload_json"] = json.dumps(data)

            return session.post(
                url,
                headers=headers,
                data=form_data,
                files=files,
                timeout=DISCORD_MESSAGE_TIMEOUT_SEC,
            )

        headers["Content-Type"] = "application/json"
        return session.post(
            url,
            headers=headers,
            data=json.dumps(data),
            timeout=DISCORD_MESSAGE_TIMEOUT_SEC,
        )
    except requests.RequestException as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_SEND_MESSAGE_REQUEST_ERROR",
                    "channel_id": str(channel_id),
                    "error": str(e),
                },
                ensure_ascii=False,
            )
        )
        return network_error_response(e)


def crosspost_message(channel_id, message_id) -> requests.Response:
    """공지 채널 메시지를 팔로우한 서버로 게시합니다. 네트워크 오류가 나면 예외 대신 상태 코드 599인 Response를 반환합니다."""
    try:
        return session.post(
            f"{DISCORD_API_BASE_URL}/channels/{channel_id}/messages/{message_id}/crosspost",
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
            timeout=DISCORD_API_TIMEOUT_SEC,
        )
    except requests.RequestException as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_CROSSPOST_REQUEST_ERROR",
                    "channel_id": str(channel_id),
                    "message_id": str(message_id),
                    "error": str(e),
                },
                ensure_ascii=False,
            )
        )
        return network_error_response(e)


def get_channel(channel_id, token=DISCORD_TOKEN) -> dict | None:
    """채널 정보를 가져옵니다. 채널이 없거나 접근할 수 없으면 None을 반환합니다.
    네트워크 오류가 나면 DiscordApiUnavailableError(502)를 던집니다.
    """
    try:
        res = session.get(
            f"{DISCORD_API_BASE_URL}/channels/{channel_id}",
            headers={
                "Authorization": f"Bot {token}",
            },
            timeout=DISCORD_API_TIMEOUT_SEC,
        )
    except requests.RequestException as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_GET_CHANNEL_REQUEST_ERROR",
                    "channel_id": str(channel_id),
                    "error": str(e),
                },
                ensure_ascii=False,
            )
        )
        raise DiscordApiUnavailableError() from e
    if res.status_code != 200:
        return None

    return res.json()


class AdminGuildsResult(NamedTuple):
    guilds: list[PartialGuild] | None
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
            res = session.get(
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

    # 관리자 권한이 있는 서버만 남긴다. v10의 permissions는 10진수 문자열이다.
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


def admin_guilds_error(result: AdminGuildsResult) -> BaseException:
    """get_admin_guilds 실패 결과를 API 응답으로 보낼 예외로 바꿉니다."""
    if result.status_code == 429:
        return RateLimitError(retry_after=result.retry_after)
    # 유저 토큰이 만료되었거나 guilds scope가 없다. 401을 받은 프론트엔드는 다시 로그인시킨다.
    if result.status_code in (401, 403):
        return UnauthorizedError(
            "디스코드 로그인이 만료되었습니다. 다시 로그인해 주세요."
        )
    return DiscordApiUnavailableError()


def is_guild_admin(guild_id: str, token: str, retry: int = 3) -> bool:
    """유저가 해당 디스코드 서버의 관리자인지 확인합니다.

    디스코드에서 서버 목록을 가져오지 못하면 admin_guilds_error의 예외를 올립니다.
    """
    result = get_admin_guilds(token, retry=retry)
    if result.guilds is None:
        raise admin_guilds_error(result)

    return any(guild["id"] == guild_id for guild in result.guilds)
