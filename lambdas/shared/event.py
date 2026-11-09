import json

from shared.exceptions import BadRequestError

# API Gateway는 headers, pathParameters, body가 없으면 키를 빼지 않고 null을 보낸다.


def get_token(event: dict) -> str | None:
    """요청 헤더에서 유저의 디스코드 OAuth 토큰(`Authorization`)을 꺼냅니다."""
    return event.get("headers", {}).get("Authorization")


def get_path_param(event: dict, name: str) -> str | None:
    return (event.get("pathParameters") or {}).get(name)


def get_json_body(event: dict) -> dict:
    """JSON body를 dict로 반환합니다. body가 없으면 {}를 반환합니다.

    JSON이 아니거나 객체가 아니면 BadRequestError를 올립니다.
    """
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError as e:
        raise BadRequestError() from e
    if not isinstance(body, dict):
        raise BadRequestError()
    return body


def get_guild_id(event: dict) -> str | None:
    """path parameter에서 먼저 찾고, 없으면 JSON body에서 찾습니다."""
    return get_path_param(event, "guild_id") or get_json_body(event).get("guild_id")
