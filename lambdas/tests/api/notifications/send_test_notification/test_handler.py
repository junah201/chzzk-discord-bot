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
def test_chzzk_lookup_failure_is_502(ddb, get_chzzk):
    put_noti(ddb.table)
    get_chzzk.return_value = None

    res, body = call()

    assert res["statusCode"] == 502
    assert body["code"] == "CHZZK_CHANNEL_UNAVAILABLE"
    assert body["message"] == (
        "치지직에서 채널 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요."
    )


@pytest.mark.usefixtures("mock_requests")
def test_missing_notification_is_404():
    res, body = call()

    assert res["statusCode"] == 404
    assert body["code"] == "NOTIFICATION_NOT_FOUND"


@pytest.mark.usefixtures("mock_requests")
def test_notification_of_other_guild_is_404(ddb):
    put_noti(ddb.table)

    res, body = call(guild_id="2")

    assert res["statusCode"] == 404
    assert body["code"] == "NOTIFICATION_NOT_FOUND"
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


@pytest.mark.parametrize(
    ("noti_attrs", "url", "discord_error", "status", "code"),
    [
        (
            {},
            MESSAGE_URL,
            {"code": 10003, "message": "Unknown Channel"},
            404,
            "DISCORD_CHANNEL_NOT_FOUND",
        ),
        (
            {"is_subscription_active": True, "webhook_url": WEBHOOK_URL},
            WEBHOOK_URL,
            {"code": 10015, "message": "Unknown Webhook"},
            500,
            "TEST_NOTIFICATION_WEBHOOK_FAILED",
        ),
    ],
    ids=["deleted-channel", "deleted-webhook"],
)
def test_discord_404_keeps_notification(
    ddb, mock_requests, noti_attrs, url, discord_error, status, code
):
    put_noti(ddb.table, **noti_attrs)
    mock_requests.post(url, status=404, json=discord_error)

    res, body = call()

    assert res["statusCode"] == status
    assert body["code"] == code
    assert get_noti(ddb.table) == {
        "PK": f"CHZZK#{CHZZK_ID}",
        "SK": f"NOTI#{CHANNEL_ID}",
        "type": "NOTI",
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL_ID,
        "custom_message": "@everyone 방송 시작!",
        "disable_embed": False,
        "disable_button": False,
        **noti_attrs,
    }


def test_other_send_failure_is_500_and_keeps_notification(ddb, mock_requests):
    put_noti(ddb.table)
    mock_requests.post(MESSAGE_URL, status=403, json={"message": "Missing Permissions"})

    res, body = call()

    assert res["statusCode"] == 500
    assert body["code"] == "TEST_NOTIFICATION_FAILED"
    assert body["message"] == (
        "테스트 알림을 보내지 못했습니다. 치직 봇의 채널 권한을 확인해 주세요."
    )
    assert body["discord_message"] == "Missing Permissions"
    assert get_noti(ddb.table) is not None


def test_webhook_send_failure_points_to_webhook(ddb, mock_requests):
    put_noti(ddb.table, is_subscription_active=True, webhook_url=WEBHOOK_URL)
    mock_requests.post(
        WEBHOOK_URL, status=401, json={"message": "Invalid Webhook Token"}
    )

    res, body = call()

    assert res["statusCode"] == 500
    assert body["code"] == "TEST_NOTIFICATION_WEBHOOK_FAILED"
    assert body["discord_message"] == "Invalid Webhook Token"
    assert body["message"] == (
        "커스텀 웹훅으로 테스트 알림을 보내지 못했습니다. 웹훅 URL을 확인해 주세요."
    )
