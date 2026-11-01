import json
from collections.abc import Iterable
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo


def pick(data: dict[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    """
    딕셔너리에서 지정된 키(keys)만 추출하여 새로운 딕셔너리를 반환합니다.
    데이터에 해당 키가 없으면 무시합니다.

    Usage:
        pick(user_data, ['id', 'name'])
    """
    if not data:
        return {}

    return {k: data[k] for k in keys if k in data}


def omit(data: dict[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    """
    딕셔너리에서 지정된 키(keys)를 제외한 나머지 데이터를 반환합니다.

    Usage:
        omit(user_data, ['password', 'private_token'])
    """
    if not data:
        return {}

    keys_set = set(keys)
    return {k: v for k, v in data.items() if k not in keys_set}


def build_response(status_code: int, message: str = None, data: dict | list = None):
    """
    공통 Lambda HTTP 응답 생성 함수
    """

    if status_code == 204:
        return {"statusCode": 204}

    body = {}
    if message:
        body["message"] = message
    # 빈 리스트/딕셔너리도 그대로 반환해야 목록 API가 []를 응답한다.
    if data is not None:
        body = data

    return {
        "statusCode": status_code,
        "body": json.dumps(body, ensure_ascii=False),
    }


def mask_secret(value: str | None, visible: int = 4) -> str | None:
    """
    로그에 남길 비밀 값(세션 쿠키, 토큰 등)을 앞뒤 일부만 남기고 가립니다.
    값이 짧으면 전부 가리고, 빈 값은 그대로 반환합니다.

    Usage:
        mask_secret("abcdefghijkl")  # "abcd...ijkl"
    """
    if not value:
        return value
    if len(value) <= visible * 2:
        return "***"
    return f"{value[:visible]}...{value[-visible:]}"


UTC = ZoneInfo("UTC")
KST = ZoneInfo("Asia/Seoul")


def to_kst_string(utc_dt_input, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    UTC 시간(datetime 객체 또는 ISO 형식 문자열)을
    유저가 보기 편한 KST 문자열로 변환합니다.
    """
    if not utc_dt_input:
        return ""

    # 만약 문자열(ISO 포맷)로 들어왔다면 datetime 객체로 파싱
    if isinstance(utc_dt_input, str):
        # 'Z' 표기법 처리를 위해 파싱 전 정리
        utc_dt = datetime.fromisoformat(utc_dt_input.replace("Z", "+00:00"))
    elif isinstance(utc_dt_input, datetime):
        utc_dt = utc_dt_input
    else:
        return str(utc_dt_input)

    # 타임존이 없는 naive datetime이라면 UTC로 가정
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=UTC)

    # KST로 변환
    kst_dt = utc_dt.astimezone(KST)

    return kst_dt.strftime(format_str)
