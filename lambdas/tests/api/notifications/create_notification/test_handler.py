import importlib
import json

import pytest
from shared import notification_dispatcher
from shared.exceptions import BadRequestError, DiscordApiUnavailableError

create_notification = importlib.import_module("api.notifications.create_notification")
service = importlib.import_module("api.notifications.create_notification.service")
client = importlib.import_module("api.notifications.create_notification.client")

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"
CHANNEL_ID = "10"
# int(CHZZK_ID, 16) % 7 == 1 → 네이버 계정 1번
CHZZK_ID = "00000000000000000000000000000001"
WEBHOOK_URL = "https://discord.com/api/webhooks/1/token"
CHZZK_DATA = {
    "liveId": 123,
    "liveTitle": "방송 제목",
    "channel": {
        "channelId": CHZZK_ID,
        "channelName": "스트리머",
        "channelImageUrl": "https://example.com/a.png",
    },
}


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(service, "dynamodb", dynamodb_table.client)
    mocker.patch.object(service, "table", dynamodb_table.table)
    mocker.patch.object(notification_dispatcher, "table", dynamodb_table.table)
    for index in range(7):
        dynamodb_table.table.put_item(
            Item={
                "PK": "NAVER#ACCOUNTS",
                "SK": f"NAVER#{index}",
                "type": "NAVER",
                "NID_AUT": f"fake-aut-{index}",
                "NID_SES": f"fake-ses-{index}",
            }
        )
    return dynamodb_table


@pytest.fixture(autouse=True)
def get_channel(mocker):
    return mocker.patch.object(
        create_notification,
        "get_channel",
        return_value={"id": CHANNEL_ID, "guild_id": GUILD_ID, "name": "알림-채널"},
    )


@pytest.fixture(autouse=True)
def verify_webhook(mocker):
    return mocker.patch.object(create_notification, "verify_webhook_guild")


@pytest.fixture(autouse=True)
def get_chzzk(mocker):
    return mocker.patch.object(
        create_notification, "get_chzzk", return_value=CHZZK_DATA
    )


@pytest.fixture(autouse=True)
def follow(mocker):
    return mocker.patch.object(
        client, "follow_chzzk_channel", return_value=(True, 200, "")
    )


@pytest.fixture(autouse=True)
def alert(mocker):
    return mocker.patch.object(client, "send_message")


def call(**body):
    payload = {"chzzk_id": CHZZK_ID, "guild_id": GUILD_ID, "channel_id": CHANNEL_ID}
    payload.update(body)
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "body": json.dumps({k: v for k, v in payload.items() if v is not None}),
    }
    res = create_notification.handler(event, None)
    return res, json.loads(res["body"]) if "body" in res else None


def put_guild(table, current_count=0, max_limit=5):
    table.put_item(
        Item={
            "PK": f"GUILD#{GUILD_ID}",
            "SK": f"GUILD#{GUILD_ID}",
            "type": "GUILD",
            "guild_id": GUILD_ID,
            "current_count": current_count,
            "max_limit": max_limit,
        }
    )


def put_subscription(table):
    table.put_item(
        Item={
            "PK": f"GUILD#{GUILD_ID}",
            "SK": "SUB#CURRENT",
            "type": "SUBSCRIPTION",
            "guild_id": GUILD_ID,
            "status": "ACTIVE",
            "expires_at": "2099-01-01T00:00:00+00:00",
        }
    )


def get_item(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk}).get("Item")


def get_guild(table):
    return get_item(table, f"GUILD#{GUILD_ID}", f"GUILD#{GUILD_ID}")


def get_noti(table, chzzk_id=CHZZK_ID):
    return get_item(table, f"CHZZK#{chzzk_id}", f"NOTI#{CHANNEL_ID}")


class TestSuccess:
    def test_registers_new_channel_and_notification(self, ddb, follow):
        res, body = call(custom_message="방송 시작!")

        assert res["statusCode"] == 204
        assert body is None
        chzzk = get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}")
        assert (chzzk["index"], chzzk["lastLiveId"]) == (1, 123)
        assert (chzzk["channelName"], chzzk["lastLiveTitle"]) == (
            "스트리머",
            "방송 제목",
        )
        noti = get_noti(ddb.table)
        assert (noti["guild_id"], noti["channel_name"]) == (GUILD_ID, "알림-채널")
        # 디스코드 채널 정보와 치지직 채널 정보가 뒤바뀌지 않았는지 함께 확인한다.
        assert (noti["chzzk_name"], noti["chzzk_id"]) == ("스트리머", CHZZK_ID)
        assert noti["custom_message"] == "방송 시작!"
        guild = get_guild(ddb.table)
        assert (guild["current_count"], guild["max_limit"]) == (1, 5)
        follow.assert_called_once_with(CHZZK_ID, "fake-aut-1", "fake-ses-1")

    def test_existing_guild_count_increments(self, ddb):
        put_guild(ddb.table, current_count=2, max_limit=10)

        res, _ = call()

        assert res["statusCode"] == 204
        guild = get_guild(ddb.table)
        assert (guild["current_count"], guild["max_limit"]) == (3, 10)

    def test_registered_channel_is_not_registered_again(self, ddb, follow):
        ddb.table.put_item(
            Item={
                "PK": f"CHZZK#{CHZZK_ID}",
                "SK": f"CHZZK#{CHZZK_ID}",
                "type": "CHZZK",
                "index": 6,
                "lastLiveId": 999,
            }
        )

        res, _ = call()

        assert res["statusCode"] == 204
        chzzk = get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}")
        assert (chzzk["index"], chzzk["lastLiveId"]) == (6, 999)
        # 현재 동작: 저장된 index(6)가 아니라 새로 계산한 index(1) 계정으로 팔로우한다.
        # live_check는 6번 계정으로 이 채널을 확인하므로 1번 계정의 팔로우는 낭비일 수 있다.
        follow.assert_called_once_with(CHZZK_ID, "fake-aut-1", "fake-ses-1")

    @pytest.mark.parametrize(
        ("chzzk_id", "index"),
        [
            ("00000000000000000000000000000000", 0),
            ("00000000000000000000000000000003", 5),
            ("00000000000000000000000000000004", 5),
            ("00000000000000000000000000000006", 6),
        ],
        ids=["0", "3-is-full", "4-is-full", "6"],
    )
    def test_account_index_skips_full_accounts(
        self, ddb, follow, get_chzzk, chzzk_id, index
    ):
        # int(chzzk_id, 16) % 7로 계정을 고르고, 가득 찬 3·4번은 건너뛴다.
        get_chzzk.return_value = {
            **CHZZK_DATA,
            "channel": {**CHZZK_DATA["channel"], "channelId": chzzk_id},
        }

        res, _ = call(chzzk_id=chzzk_id)

        assert res["statusCode"] == 204
        chzzk = get_item(ddb.table, f"CHZZK#{chzzk_id}", f"CHZZK#{chzzk_id}")
        assert chzzk["index"] == index
        assert follow.call_args.args[1] == f"fake-aut-{index}"

    def test_subscriber_options_are_saved(self, ddb, verify_webhook):
        put_subscription(ddb.table)

        res, _ = call(webhook_url=f" {WEBHOOK_URL} ", embed_color="#FF0000")

        assert res["statusCode"] == 204
        verify_webhook.assert_called_once_with(WEBHOOK_URL, GUILD_ID)
        noti = get_noti(ddb.table)
        assert noti["webhook_url"] == WEBHOOK_URL
        assert noti["embed_color"] == "#FF0000"
        assert noti["is_subscription_active"] is True


class TestValidation:
    @pytest.mark.parametrize("missing", ["chzzk_id", "guild_id", "channel_id"])
    def test_missing_field_is_400(self, get_channel, missing):
        # guild_id가 body에 없으면 middleware가 먼저 400을 반환한다.
        res, body = call(**{missing: None})

        assert res["statusCode"] == 400
        assert body["code"] == "INVALID_REQUEST"
        get_channel.assert_not_called()

    @pytest.mark.parametrize(
        ("body", "code", "message"),
        [
            (
                {"webhook_url": "https://example.com/hook"},
                "INVALID_WEBHOOK_URL",
                "디스코드 웹훅 URL 형식이 아닙니다.",
            ),
            (
                {"webhook_url": WEBHOOK_URL},
                "SUBSCRIPTION_REQUIRED",
                "커스텀 웹훅은 월간 구독 서버 전용 기능입니다.",
            ),
            (
                {"embed_color": "red"},
                "INVALID_EMBED_COLOR",
                "임베드 색상은 #RRGGBB 형식으로 입력해 주세요.",
            ),
            (
                {"embed_color": "#FF0000"},
                "SUBSCRIPTION_REQUIRED",
                "커스텀 임베드 색상은 월간 구독 서버 전용 기능입니다.",
            ),
        ],
        ids=[
            "invalid-webhook",
            "webhook-without-subscription",
            "invalid-color",
            "color-without-subscription",
        ],
    )
    def test_subscriber_option_errors(
        self, ddb, get_channel, verify_webhook, body, code, message
    ):
        res, response = call(**body)

        assert res["statusCode"] == 400
        assert response["code"] == code
        assert response["message"] == message
        get_channel.assert_not_called()
        verify_webhook.assert_not_called()
        assert get_noti(ddb.table) is None

    def test_webhook_verification_error_stops_registration(
        self, ddb, get_channel, verify_webhook
    ):
        put_subscription(ddb.table)
        verify_webhook.side_effect = BadRequestError("다른 서버")

        res, response = call(webhook_url=WEBHOOK_URL)

        assert res["statusCode"] == 400
        assert response["message"] == "다른 서버"
        get_channel.assert_not_called()
        assert get_noti(ddb.table) is None

    def test_blank_subscriber_options_are_ignored(self, ddb, verify_webhook):
        res, _ = call(webhook_url="  ", embed_color="")

        assert res["statusCode"] == 204
        assert "webhook_url" not in get_noti(ddb.table)
        verify_webhook.assert_not_called()


class TestDiscordChannel:
    def test_inaccessible_channel_is_400(self, ddb, get_channel, follow):
        get_channel.return_value = None

        res, body = call()

        assert res["statusCode"] == 400
        assert body["code"] == "BOT_CHANNEL_ACCESS_DENIED"
        assert body["message"].startswith("치직 봇이 이 채널에 접근할 수 없습니다.")
        follow.assert_not_called()

    def test_channel_of_other_guild_is_400(self, get_channel, follow):
        get_channel.return_value = {"id": CHANNEL_ID, "guild_id": "999"}

        res, body = call()

        assert res["statusCode"] == 400
        assert body["code"] == "DISCORD_CHANNEL_GUILD_MISMATCH"
        follow.assert_not_called()

    def test_discord_unreachable_is_502(self, get_channel, follow):
        get_channel.side_effect = DiscordApiUnavailableError()

        res, body = call()

        assert res["statusCode"] == 502
        assert body["code"] == "DISCORD_API_ERROR"
        follow.assert_not_called()


class TestLimitAndChzzk:
    def test_guild_limit_reached_is_400(self, ddb, get_chzzk, follow):
        put_guild(ddb.table, current_count=5, max_limit=5)

        res, body = call()

        assert res["statusCode"] == 400
        assert body["code"] == "NOTIFICATION_LIMIT_REACHED"
        assert (body["max_limit"], body["current_count"]) == (5, 5)
        assert body["message"] == ("알림 슬롯 5개를 모두 사용했습니다.")
        get_chzzk.assert_not_called()
        follow.assert_not_called()

    def test_unknown_chzzk_channel_is_400(self, ddb, get_chzzk, follow):
        get_chzzk.return_value = None

        res, body = call()

        assert res["statusCode"] == 400
        assert body["code"] == "CHZZK_CHANNEL_NOT_FOUND"
        assert (
            body["message"] == "치지직 채널을 찾지 못했습니다. 채널 ID를 확인해 주세요."
        )
        follow.assert_not_called()
        assert get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}") is None

    def test_chzzk_register_failure_is_500(self, mocker, ddb, follow):
        mocker.patch.object(
            create_notification, "register_chzzk_channel", return_value=False
        )

        res, body = call()

        assert res["statusCode"] == 500
        assert body["code"] == "CHZZK_CHANNEL_REGISTER_FAILED"
        follow.assert_not_called()
        assert get_noti(ddb.table) is None


class TestFollow:
    def test_missing_naver_account_is_500(self, ddb, follow):
        ddb.table.delete_item(Key={"PK": "NAVER#ACCOUNTS", "SK": "NAVER#1"})

        res, body = call()

        assert res["statusCode"] == 500
        assert body["message"].endswith("(1)")
        follow.assert_not_called()
        assert get_noti(ddb.table) is None

    @pytest.mark.parametrize(
        ("err_message", "status", "code", "prefix"),
        [
            (
                "채널에서 영구 활동 제한된 사용자입니다.",
                403,
                "SERVICE_ACCOUNT_BLOCKED",
                "서비스 계정이 이 치지직 채널에서 차단되었습니다.",
            ),
            (
                "최대 팔로우 수를 초과했습니다.",
                503,
                "SERVICE_FOLLOW_LIMIT_REACHED",
                "서비스 계정의 팔로우 한도가 가득 찼습니다.",
            ),
            (
                "TimeoutError: read timed out",
                500,
                None,
                "치지직 채널 팔로우 처리에 실패했습니다.",
            ),
        ],
        ids=["blocked", "follow-limit", "other"],
    )
    def test_follow_failure(
        self, ddb, follow, alert, err_message, status, code, prefix
    ):
        follow.return_value = (False, 400, err_message)

        res, body = call()

        assert res["statusCode"] == status
        assert body.get("code") == code
        if code:
            assert body["account_index"] == 1
        assert body["message"].startswith(prefix)
        assert body["message"].endswith("(1)")
        assert get_noti(ddb.table) is None
        alert.assert_called_once()
        assert alert.call_args.kwargs["token"] == client.ADMIN_DISCORD_TOKEN
        fields = {
            f["name"]: f["value"]
            for f in alert.call_args.kwargs["data"]["embeds"][0]["fields"]
        }
        assert fields == {
            "chzzk_id": CHZZK_ID,
            "status_code": "400",
            "err_message": err_message,
            "index": "1",
        }

    def test_follow_failure_keeps_registered_channel(self, ddb, follow):
        # 현재 동작: CHZZK 등록 후 팔로우가 실패해도 CHZZK 항목은 남는다.
        follow.return_value = (False, 500, "UnknownError")

        call()

        assert get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}")


class TestDuplicate:
    def test_duplicate_notification_is_400(self, ddb):
        call()

        res, body = call()

        assert res["statusCode"] == 400
        assert body["code"] == "NOTIFICATION_ALREADY_EXISTS"
        assert body["message"].startswith(
            "이 디스코드 채널에 이미 등록된 치지직 채널입니다."
        )
        assert get_guild(ddb.table)["current_count"] == 1

    def test_same_channel_registered_by_other_guild_is_500(self, ddb):
        # 현재 동작: 중복 확인은 같은 서버만 보지만, NOTI 키는 (치지직, 디스코드 채널)이라
        # 다른 서버의 같은 키가 있으면 저장 트랜잭션이 실패해 500이 된다.
        ddb.table.put_item(
            Item={
                "PK": f"CHZZK#{CHZZK_ID}",
                "SK": f"NOTI#{CHANNEL_ID}",
                "type": "NOTI",
                "guild_id": "999",
            }
        )

        res, _ = call()

        assert res["statusCode"] == 500
        # 트랜잭션이 취소되므로 다른 서버의 알림은 그대로고, 이 서버의 GUILD도 만들어지지 않는다.
        assert get_noti(ddb.table)["guild_id"] == "999"
        assert get_guild(ddb.table) is None


class TestAutoCrosspost:
    ANNOUNCEMENT_CHANNEL = {
        "id": CHANNEL_ID,
        "guild_id": GUILD_ID,
        "name": "공지",
        "type": 5,
    }

    def test_announcement_channel_is_saved(self, ddb, get_channel):
        put_subscription(ddb.table)
        get_channel.return_value = self.ANNOUNCEMENT_CHANNEL

        res, _ = call(auto_crosspost=True)

        assert res["statusCode"] == 204
        noti = get_noti(ddb.table)
        assert noti["auto_crosspost"] is True
        assert noti["is_subscription_active"] is True

    def test_disabled_option_is_not_saved(self, ddb):
        res, _ = call(auto_crosspost=False)

        assert res["statusCode"] == 204
        noti = get_noti(ddb.table)
        assert "auto_crosspost" not in noti
        assert "is_subscription_active" not in noti

    def test_without_subscription_is_400(self, ddb, get_channel):
        get_channel.return_value = self.ANNOUNCEMENT_CHANNEL

        res, body = call(auto_crosspost=True)

        assert res["statusCode"] == 400
        assert body["code"] == "SUBSCRIPTION_REQUIRED"
        assert (
            body["message"] == "공지 채널 자동 게시는 월간 구독 서버 전용 기능입니다."
        )
        get_channel.assert_not_called()
        assert get_noti(ddb.table) is None

    def test_text_channel_is_400(self, ddb, follow):
        put_subscription(ddb.table)

        res, body = call(auto_crosspost=True)

        assert res["statusCode"] == 400
        assert body["code"] == "CROSSPOST_REQUIRES_ANNOUNCEMENT_CHANNEL"
        follow.assert_not_called()
        assert get_noti(ddb.table) is None
