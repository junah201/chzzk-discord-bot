from datetime import datetime

from shared.discord import BUTTON_STYLE, COMPONENT_TYPE
from shared.notification_dispatcher import get_embed_color, get_embed_fields

ANONYMOUS_PROFILE_IMAGE_URL = "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na"


def build_live_message(
    chzzk_id: str,
    chzzk: dict,
    notification_item: dict,
    *,
    content: str,
    now: datetime,
) -> dict:
    """방송 시작 알림 메시지를 만듭니다. notification_item은 DynamoDB client 형식의 NOTI 아이템입니다."""
    live_url = f"https://chzzk.naver.com/live/{chzzk_id}"
    channel = chzzk["channel"]
    data = {"content": content}

    if not notification_item.get("disable_embed", {"BOOL": False})["BOOL"]:
        data["embeds"] = [
            {
                "title": f"{chzzk['liveTitle']}",
                "description": f"{channel['channelName']} 님이 방송을 시작했습니다.",
                "color": get_embed_color(notification_item),
                "fields": get_embed_fields(chzzk, notification_item),
                "image": {
                    "url": (
                        chzzk["liveImageUrl"] or channel["channelImageUrl"] or ""
                    ).replace("_{type}", "_1080"),
                },
                "author": {
                    "name": f"{channel['channelName']}",
                    "url": live_url,
                    "icon_url": channel["channelImageUrl"]
                    or ANONYMOUS_PROFILE_IMAGE_URL,
                },
                "footer": {"text": "chzzk.junah.dev"},
                "url": live_url,
                "timestamp": now.isoformat(),
            },
        ]

    if not notification_item.get("disable_button", {"BOOL": False})["BOOL"]:
        data["components"] = [
            {
                "type": COMPONENT_TYPE.ACTION_ROW,
                "components": [
                    {
                        "type": COMPONENT_TYPE.BUTTON,
                        "label": "바로가기",
                        "style": BUTTON_STYLE.LINK,
                        "url": live_url,
                    }
                ],
            },
        ]

    return data
