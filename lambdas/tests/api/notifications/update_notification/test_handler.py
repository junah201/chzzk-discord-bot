import importlib
import json

import pytest
from botocore.exceptions import ClientError
from shared import notification_dispatcher
from shared.exceptions import BadRequestError

update_notification = importlib.import_module("api.notifications.update_notification")

pytestmark = pytest.mark.usefixtures("as_admin")

GUILD_ID = "1"
CHANNEL_ID = "10"
CHZZK_ID = "abc"
WEBHOOK_URL = "https://discord.com/api/webhooks/1/token"


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(update_notification, "dynamodb", dynamodb_table.client)
    mocker.patch.object(notification_dispatcher, "table", dynamodb_table.table)
    return dynamodb_table


@pytest.fixture(autouse=True)
def verify_webhook(mocker):
    return mocker.patch.object(update_notification, "verify_webhook_guild")


def call(**body):
    payload = {"chzzk_id": CHZZK_ID, "guild_id": GUILD_ID, "channel_id": CHANNEL_ID}
    payload.update(body)
    event = {
        "headers": {"Authorization": "Bearer user-token"},
        "body": json.dumps({k: v for k, v in payload.items() if v is not None}),
    }
    res = update_notification.handler(event, None)
    return res, json.loads(res["body"]) if "body" in res else None


def put_guild(table, current_count=1, max_limit=5):
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


def put_noti(table, guild_id=GUILD_ID, **attrs):
    table.put_item(
        Item={
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"NOTI#{CHANNEL_ID}",
            "type": "NOTI",
            "guild_id": guild_id,
            "channel_id": CHANNEL_ID,
            "custom_message": "예전 메시지",
            "disable_embed": False,
            "disable_button": False,
            "disable_notification": False,
            **attrs,
        }
    )


def get_noti(table):
    return table.get_item(Key={"PK": f"CHZZK#{CHZZK_ID}", "SK": f"NOTI#{CHANNEL_ID}"})[
        "Item"
    ]


@pytest.fixture
def setup(ddb):
    put_guild(ddb.table)
    put_noti(ddb.table)
    return ddb


class TestSuccess:
    def test_updates_options(self, setup):
        res, body = call(
            custom_message="새 메시지",
            disable_embed=True,
            disable_button=True,
            disable_notification=True,
        )

        assert res["statusCode"] == 204
        assert body is None
        noti = get_noti(setup.table)
        assert noti["custom_message"] == "새 메시지"
        assert (
            noti["disable_embed"],
            noti["disable_button"],
            noti["disable_notification"],
        ) == (True, True, True)
        assert noti["is_subscription_active"] is False

    @pytest.mark.parametrize(
        "flag",
        ["disable_embed", "disable_button", "disable_tag", "disable_notification"],
    )
    def test_each_flag_is_saved_to_its_own_attribute(self, setup, flag):
        call(**{flag: True})

        noti = get_noti(setup.table)
        flags = (
            "disable_embed",
            "disable_button",
            "disable_tag",
            "disable_notification",
        )
        assert {f: noti[f] for f in flags} == {f: f == flag for f in flags}

    def test_missing_options_reset_to_defaults(self, setup):
        put_noti(setup.table, disable_embed=True, custom_message="예전 메시지")

        call()

        noti = get_noti(setup.table)
        assert noti["custom_message"] == ""
        assert noti["disable_embed"] is False

    def test_keeps_other_attributes(self, setup):
        put_noti(setup.table, chzzk_name="스트리머", noti_fail_count=2)

        call(custom_message="x")

        noti = get_noti(setup.table)
        assert (noti["chzzk_name"], noti["noti_fail_count"]) == ("스트리머", 2)

    def test_backfills_chzzk_id_on_legacy_notification(self, setup):
        assert "chzzk_id" not in get_noti(setup.table)

        call()

        assert get_noti(setup.table)["chzzk_id"] == CHZZK_ID

    def test_subscriber_options_are_saved(self, setup, verify_webhook):
        put_subscription(setup.table)

        res, _ = call(webhook_url=f" {WEBHOOK_URL} ", embed_color=" #FF0000 ")

        assert res["statusCode"] == 204
        verify_webhook.assert_called_once_with(WEBHOOK_URL, GUILD_ID)
        noti = get_noti(setup.table)
        assert noti["webhook_url"] == WEBHOOK_URL
        assert noti["embed_color"] == "#FF0000"
        assert noti["is_subscription_active"] is True

    def test_empty_embed_color_clears_saved_color(self, setup):
        put_noti(setup.table, embed_color="#FF0000")

        res, _ = call(embed_color="")

        assert res["statusCode"] == 204
        assert get_noti(setup.table)["embed_color"] == ""

    def test_omitted_embed_color_is_kept(self, setup):
        put_noti(setup.table, embed_color="#FF0000")

        call()

        assert get_noti(setup.table)["embed_color"] == "#FF0000"

    @pytest.mark.parametrize("value", ["", "   "], ids=["empty", "blank"])
    def test_empty_webhook_url_clears_saved_webhook(self, setup, verify_webhook, value):
        put_noti(setup.table, webhook_url=WEBHOOK_URL)

        res, _ = call(webhook_url=value)

        assert res["statusCode"] == 204
        verify_webhook.assert_not_called()
        assert get_noti(setup.table)["webhook_url"] == ""

    def test_clearing_webhook_does_not_need_subscription(self, setup):
        # 구독이 만료된 서버도 남아 있는 웹훅을 지울 수 있어야 한다.
        put_noti(setup.table, webhook_url=WEBHOOK_URL, is_subscription_active=True)

        res, _ = call(webhook_url="")

        assert res["statusCode"] == 204
        noti = get_noti(setup.table)
        assert noti["webhook_url"] == ""
        assert noti["is_subscription_active"] is False

    def test_omitted_webhook_url_is_kept(self, setup):
        put_noti(setup.table, webhook_url=WEBHOOK_URL)

        call(custom_message="x")

        assert get_noti(setup.table)["webhook_url"] == WEBHOOK_URL

    def test_count_at_limit_can_update(self, ddb):
        put_guild(ddb.table, current_count=5, max_limit=5)
        put_noti(ddb.table)

        res, _ = call(custom_message="x")

        assert res["statusCode"] == 204


class TestValidation:
    @pytest.mark.parametrize("missing", ["chzzk_id", "guild_id", "channel_id"])
    def test_missing_field_is_400(self, setup, missing):
        res, body = call(**{missing: None})

        assert res["statusCode"] == 400
        assert body["code"] == "INVALID_REQUEST"
        assert get_noti(setup.table)["custom_message"] == "예전 메시지"

    @pytest.mark.parametrize(
        ("body", "message"),
        [
            (
                {"webhook_url": "https://example.com/hook"},
                "유효한 디스코드 웹훅 URL을 입력해주세요.",
            ),
            (
                {"webhook_url": WEBHOOK_URL},
                "커스텀 웹훅은 활성 월간 정기 구독 서버에서만 사용할 수 있습니다.",
            ),
            (
                {"embed_color": "red"},
                "임베드 색상은 #RRGGBB 형식 또는 0~16777215 사이의 숫자여야 합니다.",
            ),
            (
                {"embed_color": "#FF0000"},
                "커스텀 임베드 색상은 활성 월간 정기 구독 서버에서만 사용할 수 있습니다.",
            ),
        ],
        ids=[
            "invalid-webhook",
            "webhook-without-subscription",
            "invalid-color",
            "color-without-subscription",
        ],
    )
    def test_subscriber_option_errors(self, setup, verify_webhook, body, message):
        res, response = call(custom_message="바뀌면 안 됨", **body)

        assert res["statusCode"] == 400
        assert response["message"] == message
        assert get_noti(setup.table)["custom_message"] == "예전 메시지"
        verify_webhook.assert_not_called()

    def test_webhook_verification_error_keeps_notification(self, setup, verify_webhook):
        put_subscription(setup.table)
        verify_webhook.side_effect = BadRequestError("다른 서버")

        res, response = call(custom_message="바뀌면 안 됨", webhook_url=WEBHOOK_URL)

        assert res["statusCode"] == 400
        assert response["message"] == "다른 서버"
        noti = get_noti(setup.table)
        assert noti["custom_message"] == "예전 메시지"
        assert "webhook_url" not in noti


class TestNotFound:
    def test_missing_guild_is_404(self, ddb):
        put_noti(ddb.table)

        res, body = call()

        assert res["statusCode"] == 404
        assert body["message"].startswith("서버 메타데이터를 찾을 수 없습니다.")

    def test_missing_notification_is_404(self, ddb):
        put_guild(ddb.table)

        res, body = call()

        assert res["statusCode"] == 404
        assert body["message"] == "알림 설정을 찾을 수 없거나 권한이 없습니다."
        assert (
            ddb.table.get_item(
                Key={"PK": f"CHZZK#{CHZZK_ID}", "SK": f"NOTI#{CHANNEL_ID}"}
            ).get("Item")
            is None
        )

    def test_notification_of_other_guild_is_404_and_unchanged(self, ddb):
        put_guild(ddb.table)
        put_noti(ddb.table, guild_id="2")

        res, _ = call(custom_message="바뀌면 안 됨")

        assert res["statusCode"] == 404
        noti = get_noti(ddb.table)
        assert (noti["guild_id"], noti["custom_message"]) == ("2", "예전 메시지")


class TestOverLimit:
    def test_over_limit_blocks_update(self, ddb):
        put_guild(ddb.table, current_count=6, max_limit=5)
        put_noti(ddb.table)

        res, body = call(custom_message="바뀌면 안 됨")

        assert res["statusCode"] == 400
        assert body["message"] == (
            "현재 서버에 등록된 알림이 제한 개수(5개)를 초과하여 설정을 수정할 수 없습니다. "
            "초과된 알림(6/5)을 정리(삭제)한 후 다시 시도해주세요."
        )
        assert get_noti(ddb.table)["custom_message"] == "예전 메시지"


def test_other_dynamodb_error_is_500(mocker, setup):
    log_error = mocker.patch.object(update_notification.logger, "error")
    mocker.patch.object(
        setup.client,
        "update_item",
        side_effect=ClientError(
            {"Error": {"Code": "ProvisionedThroughputExceededException"}},
            "UpdateItem",
        ),
    )

    res, body = call()

    assert res["statusCode"] == 500
    assert body["message"] == "알림 설정 업데이트 중 오류가 발생했습니다."
    assert (
        json.loads(log_error.call_args.args[0])["type"] == "UPDATE_NOTIFICATION_ERROR"
    )
