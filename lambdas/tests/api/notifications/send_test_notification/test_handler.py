import importlib
import json

import pytest
from shared.discord.utils import DISCORD_API_BASE_URL
from shared.notification_dispatcher import DEFAULT_EMBED_COLOR

send_test_notification = importlib.import_module(
    "api.notifications.send_test_notification"
)

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"
CHANNEL_ID = "10"
CHZZK_ID = "abcdef0123456789abcdef0123456789"
MESSAGE_URL = f"{DISCORD_API_BASE_URL}/channels/{CHANNEL_ID}/messages"
WEBHOOK_URL = "https://discord.com/api/webhooks/123/token"
LIVE_URL = f"https://chzzk.naver.com/live/{CHZZK_ID}"
CHZZK = {
    "liveId": 1,
    "liveTitle": "방송 제목",
    "liveCategoryValue": "Just Chatting",
    "liveImageUrl": "https://example.com/live_{type}.jpg",
    "channel": {
        "channelId": CHZZK_ID,
        "channelName": "스트리머",
        "channelImageUrl": "https://example.com/profile.png",
    },
}


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(send_test_notification, "dynamodb", dynamodb_table.client)
    return dynamodb_table


@pytest.fixture(autouse=True)
def get_chzzk(mocker):
    return mocker.patch.object(send_test_notification, "get_chzzk", return_value=CHZZK)


def call(**body):
    payload = {"chzzk_id": CHZZK_ID, "guild_id": GUILD_ID, "channel_id": CHANNEL_ID}
    payload.update(body)
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "body": json.dumps({k: v for k, v in payload.items() if v is not None}),
    }
    res = send_test_notification.handler(event, None)
    return res, json.loads(res["body"])


def put_noti(table, guild_id=GUILD_ID, **attrs):
    table.put_item(
        Item={
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"NOTI#{CHANNEL_ID}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": CHANNEL_ID,
            "custom_message": "@everyone 방송 시작!",
            "disable_embed": False,
            "disable_button": False,
            **attrs,
        }
    )


def get_noti(table):
    return table.get_item(
        Key={"PK": f"CHZZK#{CHZZK_ID}", "SK": f"NOTI#{CHANNEL_ID}"}
    ).get("Item")


def sent_payload(mock_requests, index=0):
    return json.loads(mock_requests.calls[index].request.body)


@pytest.mark.parametrize("missing", ["chzzk_id", "guild_id", "channel_id"])
def test_missing_field_is_400(missing):
    res, body = call(**{missing: None})

    assert res["statusCode"] == 400
    assert body["code"] == "INVALID_REQUEST"


@pytest.mark.usefixtures("mock_requests")
def test_unknown_chzzk_channel_is_400(ddb, get_chzzk):
    put_noti(ddb.table)
    get_chzzk.return_value = None

    res, body = call()

    assert res["statusCode"] == 400
    assert body["message"] == "해당 치지직 채널을 찾을 수 없습니다."


@pytest.mark.usefixtures("mock_requests")
def test_missing_notification_is_404():
    res, body = call()

    assert res["statusCode"] == 404
    assert body["message"] == "해당 알림이 존재하지 않습니다."


@pytest.mark.usefixtures("mock_requests")
def test_notification_of_other_guild_is_404(ddb):
    put_noti(ddb.table)

    res, body = call(guild_id="2")

    assert res["statusCode"] == 404
    assert body["message"] == "해당 알림이 존재하지 않습니다."
    assert get_noti(ddb.table) is not None


def test_sends_full_message_to_channel(ddb, mock_requests):
    put_noti(ddb.table)
    mock_requests.post(MESSAGE_URL, json={"id": "1"})

    res, body = call()

    assert res["statusCode"] == 200
    assert body["message"] == "테스트 알림을 성공적으로 전송했습니다."
    payload = sent_payload(mock_requests)
    assert payload["content"] == (
        "관리자의 요청에 따라 전송된 테스트 알림입니다.\n\n@everyone 방송 시작!"
    )
    [embed] = payload["embeds"]
    assert embed["title"] == "방송 제목"
    assert embed["description"] == "스트리머 님이 방송을 시작했습니다."
    assert embed["color"] == DEFAULT_EMBED_COLOR
    assert embed["image"]["url"] == "https://example.com/live_1080.jpg"
    assert embed["url"] == LIVE_URL
    [row] = payload["components"]
    assert row["components"][0]["url"] == LIVE_URL


def test_disabled_embed_and_button_are_omitted(ddb, mock_requests):
    put_noti(ddb.table, disable_embed=True, disable_button=True)
    mock_requests.post(MESSAGE_URL, json={"id": "1"})

    res, _ = call()

    assert res["statusCode"] == 200
    payload = sent_payload(mock_requests)
    assert "embeds" not in payload
    assert "components" not in payload


def test_subscriber_webhook_and_color_are_used(ddb, mock_requests):
    put_noti(
        ddb.table,
        is_subscription_active=True,
        webhook_url=WEBHOOK_URL,
        embed_color="#FF0000",
    )
    mock_requests.post(WEBHOOK_URL, status=204)

    res, _ = call()

    assert res["statusCode"] == 200
    assert sent_payload(mock_requests)["embeds"][0]["color"] == 0xFF0000


def test_deleted_discord_channel_removes_notification(ddb, mock_requests):
    # 현재 동작: 404면 알림을 지운다. (GUILD current_count는 줄이지 않는다.)
    put_noti(ddb.table)
    mock_requests.post(MESSAGE_URL, status=404, json={"code": 10003})

    res, body = call()

    assert res["statusCode"] == 404
    assert body["message"] == "해당 디스코드 채널이 존재하지 않습니다."
    assert get_noti(ddb.table) is None


def test_other_send_failure_is_500_and_keeps_notification(ddb, mock_requests):
    put_noti(ddb.table)
    mock_requests.post(MESSAGE_URL, status=403, json={"message": "Missing Permissions"})

    res, body = call()

    assert res["statusCode"] == 500
    assert "Missing Permissions" in body["message"]
    assert get_noti(ddb.table) is not None
