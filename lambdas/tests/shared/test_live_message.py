from datetime import UTC, datetime

import pytest
from shared.discord import BUTTON_STYLE, COMPONENT_TYPE
from shared.live_message import ANONYMOUS_PROFILE_IMAGE_URL, build_live_message
from shared.notification_dispatcher import DEFAULT_EMBED_COLOR

CHZZK_ID = "abcdef0123456789abcdef0123456789"
LIVE_URL = f"https://chzzk.naver.com/live/{CHZZK_ID}"
CHANNEL_IMAGE = "https://example.com/profile.png"
NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def live(**overrides):
    data = {
        "liveId": 200,
        "liveTitle": "새 방송",
        "liveCategoryValue": "Just Chatting",
        "liveImageUrl": "https://example.com/live_{type}.jpg",
        "channel": {
            "channelId": CHZZK_ID,
            "channelName": "스트리머",
            "channelImageUrl": CHANNEL_IMAGE,
        },
    }
    data.update(overrides)
    return data


def noti(**attrs):
    return {
        "disable_embed": {"BOOL": False},
        "disable_button": {"BOOL": False},
        **attrs,
    }


def build(chzzk=None, item=None, content=""):
    return build_live_message(
        CHZZK_ID,
        chzzk or live(),
        noti() if item is None else item,
        content=content,
        now=NOW,
    )


def test_full_message():
    assert build(content="@everyone 방송 시작!") == {
        "content": "@everyone 방송 시작!",
        "embeds": [
            {
                "title": "새 방송",
                "description": "스트리머 님이 방송을 시작했습니다.",
                "color": DEFAULT_EMBED_COLOR,
                "fields": [{"name": "카테고리", "value": "Just Chatting"}],
                "image": {"url": "https://example.com/live_1080.jpg"},
                "author": {
                    "name": "스트리머",
                    "url": LIVE_URL,
                    "icon_url": CHANNEL_IMAGE,
                },
                "footer": {"text": "chzzk.junah.dev"},
                "url": LIVE_URL,
                "timestamp": NOW.isoformat(),
            }
        ],
        "components": [
            {
                "type": COMPONENT_TYPE.ACTION_ROW,
                "components": [
                    {
                        "type": COMPONENT_TYPE.BUTTON,
                        "label": "바로가기",
                        "style": BUTTON_STYLE.LINK,
                        "url": LIVE_URL,
                    }
                ],
            }
        ],
    }


def test_missing_flags_show_embed_and_button():
    data = build(item={})
    assert "embeds" in data
    assert "components" in data


def test_disable_embed_and_button():
    item = noti(disable_embed={"BOOL": True}, disable_button={"BOOL": True})
    assert build(item=item, content="알림") == {"content": "알림"}


@pytest.mark.parametrize(
    ("flag", "removed", "kept"),
    [
        ("disable_embed", "embeds", "components"),
        ("disable_button", "components", "embeds"),
    ],
)
def test_each_flag_removes_only_its_part(flag, removed, kept):
    data = build(item=noti(**{flag: {"BOOL": True}}))
    assert removed not in data
    assert kept in data


def test_shows_tags_by_default():
    data = build(chzzk=live(tags=["게임", "소통"]))
    assert data["embeds"][0]["fields"] == [
        {"name": "카테고리", "value": "Just Chatting"},
        {"name": "태그", "value": "`게임` `소통`"},
    ]


def test_disable_tag_hides_tags():
    data = build(chzzk=live(tags=["게임"]), item=noti(disable_tag={"BOOL": True}))
    assert data["embeds"][0]["fields"] == [
        {"name": "카테고리", "value": "Just Chatting"}
    ]


@pytest.mark.parametrize(
    ("active", "expected"), [(True, 0xFF0000), (False, DEFAULT_EMBED_COLOR)]
)
def test_subscriber_embed_color(active, expected):
    item = noti(is_subscription_active={"BOOL": active}, embed_color={"S": "#FF0000"})
    assert build(item=item)["embeds"][0]["color"] == expected


def test_image_falls_back_to_channel_image():
    data = build(chzzk=live(liveImageUrl=None))
    assert data["embeds"][0]["image"]["url"] == CHANNEL_IMAGE


def test_missing_images_use_defaults():
    chzzk = live(
        liveImageUrl=None,
        channel={
            "channelId": CHZZK_ID,
            "channelName": "스트리머",
            "channelImageUrl": None,
        },
    )
    embed = build(chzzk=chzzk)["embeds"][0]
    assert embed["image"]["url"] == ""
    assert embed["author"]["icon_url"] == ANONYMOUS_PROFILE_IMAGE_URL
