import re
from datetime import datetime, timedelta, timezone

__all__ = ["MAX_CONTENT_LENGTH", "render_message"]

MAX_CONTENT_LENGTH = 2000
KST = timezone(timedelta(hours=9))

_VARIABLE = re.compile(r"\{([a-z_.]+)\}")
_MARKDOWN = re.compile(r"([\\*_~`|>#\-\[\]()<])")


def escape_text(value: str) -> str:
    """스트리머가 정한 값이 멘션이나 마크다운으로 해석되지 않게 바꿉니다."""
    value = " ".join(value.split())
    value = _MARKDOWN.sub(r"\\\1", value)
    return value.replace("@", "@​")


def _started_at(chzzk: dict, now: datetime) -> str:
    started_at = now
    open_date = chzzk.get("openDate")
    if open_date:
        try:
            started_at = datetime.strptime(open_date, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=KST
            )
        except ValueError:
            pass
    return f"<t:{int(started_at.timestamp())}:R>"


def _variables(chzzk_id: str, chzzk: dict, now: datetime) -> dict[str, str]:
    channel = chzzk.get("channel") or {}
    category = escape_text(chzzk.get("liveCategoryValue") or "")
    tags = [escape_text(tag) for tag in chzzk.get("tags") or [] if tag]
    return {
        "channel.name": escape_text(channel.get("channelName") or ""),
        "channel.url": f"https://chzzk.naver.com/{chzzk_id}",
        "stream.url": f"https://chzzk.naver.com/live/{chzzk_id}",
        "stream.title": escape_text(chzzk.get("liveTitle") or ""),
        "stream.category": category,
        "stream.game": category,
        "stream.tags": ", ".join(tags),
        "stream.started_at": _started_at(chzzk, now),
        "everyone": "@everyone",
        "here": "@here",
    }


def render_message(template: str, chzzk_id: str, chzzk: dict, now: datetime) -> str:
    """커스텀 메시지의 {변수}를 방송 정보로 바꿉니다. 모르는 변수는 그대로 둡니다."""
    if "{" not in template:
        return template[:MAX_CONTENT_LENGTH]
    variables = _variables(chzzk_id, chzzk, now)
    rendered = _VARIABLE.sub(lambda m: variables.get(m.group(1), m.group(0)), template)
    return rendered[:MAX_CONTENT_LENGTH]
