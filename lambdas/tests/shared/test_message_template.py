from datetime import UTC, datetime

import pytest
from shared.message_template import MAX_CONTENT_LENGTH, escape_text, render_message

CHZZK_ID = "abcdef0123456789abcdef0123456789"
NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def live(**overrides):
    data = {
        "liveId": 200,
        "liveTitle": "새 방송",
        "liveCategoryValue": "Just Chatting",
        "tags": ["게임", "소통"],
        "openDate": "2026-01-02 12:00:00",
        "channel": {"channelId": CHZZK_ID, "channelName": "스트리머"},
    }
    data.update(overrides)
    return data


def render(template, chzzk=None):
    return render_message(template, CHZZK_ID, chzzk or live(), NOW)


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("{channel.name}", "스트리머"),
        ("{channel.url}", f"https://chzzk.naver.com/{CHZZK_ID}"),
        ("{stream.url}", f"https://chzzk.naver.com/live/{CHZZK_ID}"),
        ("{stream.title}", "새 방송"),
        ("{stream.category}", "Just Chatting"),
        ("{stream.game}", "Just Chatting"),
        ("{stream.tags}", "게임, 소통"),
        ("{stream.started_at}", "<t:1767322800:R>"),
        ("{everyone}", "@everyone"),
        ("{here}", "@here"),
    ],
)
def test_variables(template, expected):
    assert render(template) == expected


def test_mixed_template():
    assert (
        render("{everyone} {channel.name} 방송 시작! {stream.title}")
        == "@everyone 스트리머 방송 시작! 새 방송"
    )


def test_unknown_variable_is_kept():
    assert render("{stream.viewer_count} {foo} {Stream.Title}") == (
        "{stream.viewer_count} {foo} {Stream.Title}"
    )


def test_plain_text_is_unchanged():
    assert render("@everyone **방송** 시작") == "@everyone **방송** 시작"


def test_missing_fields_are_empty():
    chzzk = {"liveId": 1, "channel": {"channelId": CHZZK_ID}}
    assert render("[{channel.name}|{stream.title}|{stream.tags}]", chzzk) == "[||]"


def test_started_at_falls_back_to_now():
    assert render("{stream.started_at}", live(openDate=None)) == (
        f"<t:{int(NOW.timestamp())}:R>"
    )
    assert render("{stream.started_at}", live(openDate="bad")) == (
        f"<t:{int(NOW.timestamp())}:R>"
    )


def test_title_cannot_mention():
    rendered = render("{stream.title}", live(liveTitle="@everyone <@&123>"))
    assert "@everyone" not in rendered
    assert "<@&" not in rendered


def test_title_markdown_is_escaped():
    assert escape_text("**굵게** [링크](https://x.y)") == (
        r"\*\*굵게\*\* \[링크\]\(https://x.y\)"
    )


def test_title_newlines_are_collapsed():
    assert render("{stream.title}", live(liveTitle="첫 줄\n# 둘째 줄")) == (
        r"첫 줄 \# 둘째 줄"
    )


def test_result_is_truncated():
    assert len(render("{stream.title}" * 300, live(liveTitle="가" * 100))) == (
        MAX_CONTENT_LENGTH
    )
