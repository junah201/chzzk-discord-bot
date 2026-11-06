import importlib

import pytest
from shared.exceptions import BadRequestError

service = importlib.import_module("api.notifications.post_notification.service")

GUILD_ID = "1"
CHANNEL_ID = "10"
CHZZK_ID = "abcdef0123456789abcdef0123456789"
CHZZK_DATA = {
    "liveId": 123,
    "liveTitle": "방송 제목",
    "channel": {
        "channelId": CHZZK_ID,
        "channelName": "스트리머",
        "channelImageUrl": "https://example.com/a.png",
    },
}
CHANNEL_DATA = {"id": CHANNEL_ID, "name": "알림-채널"}


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(service, "dynamodb", dynamodb_table.client)
    mocker.patch.object(service, "table", dynamodb_table.table)
    return dynamodb_table


@pytest.fixture
def subscription_active(mocker):
    return mocker.patch.object(
        service, "is_guild_subscription_active", return_value=True
    )


def put_guild(table, current_count=0, max_limit=5, **attrs):
    item = {
        "PK": f"GUILD#{GUILD_ID}",
        "SK": f"GUILD#{GUILD_ID}",
        "type": "GUILD",
        "guild_id": GUILD_ID,
        "current_count": current_count,
        "max_limit": max_limit,
        **attrs,
    }
    table.put_item(Item={k: v for k, v in item.items() if v is not None})


def get_item(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk}).get("Item")


def get_guild(table):
    return get_item(table, f"GUILD#{GUILD_ID}", f"GUILD#{GUILD_ID}")


def get_noti(table, chzzk_id=CHZZK_ID, channel_id=CHANNEL_ID):
    return get_item(table, f"CHZZK#{chzzk_id}", f"NOTI#{channel_id}")


def save(body=None, channel_id=CHANNEL_ID, guild_id=GUILD_ID, chzzk_id=CHZZK_ID):
    service.save_notification_and_increment_counter(
        guild_id=guild_id,
        channel_id=channel_id,
        channel_data=CHANNEL_DATA,
        chzzk_id=chzzk_id,
        chzzk_data=CHZZK_DATA,
        body=body or {},
    )


class TestCheckGuildLimit:
    def test_new_guild_uses_default_limit(self):
        service.check_guild_limit(GUILD_ID)

    @pytest.mark.parametrize(
        ("current_count", "max_limit"), [(0, 5), (4, 5), (249, 250)]
    )
    def test_under_limit(self, ddb, current_count, max_limit):
        put_guild(ddb.table, current_count=current_count, max_limit=max_limit)

        service.check_guild_limit(GUILD_ID)

    @pytest.mark.parametrize(
        ("current_count", "max_limit"), [(5, 5), (6, 5), (250, 250)]
    )
    def test_at_or_over_limit(self, ddb, current_count, max_limit):
        put_guild(ddb.table, current_count=current_count, max_limit=max_limit)

        with pytest.raises(BadRequestError) as exc_info:
            service.check_guild_limit(GUILD_ID)

        assert exc_info.value.code == "NOTIFICATION_LIMIT_REACHED"
        assert exc_info.value.details == {
            "max_limit": max_limit,
            "current_count": current_count,
        }
        assert exc_info.value.message == (
            f"알림 슬롯 {max_limit}개를 모두 사용했습니다."
        )

    def test_missing_attributes_use_defaults(self, ddb):
        put_guild(ddb.table, current_count=None, max_limit=None)

        service.check_guild_limit(GUILD_ID)


class TestChzzkChannel:
    def test_not_registered(self):
        assert service.is_chzzk_registered(CHZZK_ID) is False

    def test_register_and_find(self, ddb):
        assert service.register_chzzk_channel(CHZZK_ID, CHZZK_DATA, 3) is True

        assert service.is_chzzk_registered(CHZZK_ID) is True
        assert get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}") == {
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"CHZZK#{CHZZK_ID}",
            "type": "CHZZK",
            "channelId": CHZZK_ID,
            "channelName": "스트리머",
            "channelImageUrl": "https://example.com/a.png",
            "lastLiveId": 123,
            "lastLiveTitle": "방송 제목",
            "index": 3,
        }

    def test_missing_image_is_saved_as_empty_string(self, ddb):
        data = {
            **CHZZK_DATA,
            "channel": {**CHZZK_DATA["channel"], "channelImageUrl": None},
        }

        service.register_chzzk_channel(CHZZK_ID, data, 0)

        item = get_item(ddb.table, f"CHZZK#{CHZZK_ID}", f"CHZZK#{CHZZK_ID}")
        assert item["channelImageUrl"] == ""

    def test_notification_item_alone_is_not_registered(self, ddb):
        save()

        assert service.is_chzzk_registered(CHZZK_ID) is False


class TestGetNaverAccount:
    def test_returns_account(self, ddb):
        account = {
            "PK": "NAVER#ACCOUNTS",
            "SK": "NAVER#2",
            "type": "NAVER",
            "NID_AUT": "fake-aut",
            "NID_SES": "fake-ses",
        }
        ddb.table.put_item(Item=account)

        assert service.get_naver_account(2) == account

    def test_missing_account(self):
        assert service.get_naver_account(2) is None


class TestIsNotificationExists:
    def test_same_guild(self):
        save()

        assert service.is_notification_exists(CHZZK_ID, CHANNEL_ID, GUILD_ID) is True

    def test_other_guild(self):
        save()

        assert service.is_notification_exists(CHZZK_ID, CHANNEL_ID, "2") is False

    @pytest.mark.parametrize(
        ("chzzk_id", "channel_id"),
        [("other", CHANNEL_ID), (CHZZK_ID, "99")],
        ids=["other-chzzk", "other-channel"],
    )
    def test_missing(self, chzzk_id, channel_id):
        save()

        assert service.is_notification_exists(chzzk_id, channel_id, GUILD_ID) is False


class TestSaveNotification:
    def test_new_guild_creates_guild_and_counts_one(self, ddb):
        save()

        guild = get_guild(ddb.table)
        assert guild["max_limit"] == 5
        assert guild["current_count"] == 1
        assert guild["type"] == "GUILD"
        assert guild["guild_id"] == GUILD_ID

    def test_existing_guild_increments_count(self, ddb):
        put_guild(ddb.table, current_count=3, max_limit=250)

        save()

        guild = get_guild(ddb.table)
        assert guild["current_count"] == 4
        assert guild["max_limit"] == 250

    def test_existing_guild_without_count_starts_from_one(self, ddb):
        put_guild(ddb.table, current_count=None)

        save()

        assert get_guild(ddb.table)["current_count"] == 1

    def test_saves_notification_with_defaults(self, ddb, subscription_active):
        save(body={})

        assert get_noti(ddb.table) == {
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"NOTI#{CHANNEL_ID}",
            "type": "NOTI",
            "chzzk_id": CHZZK_ID,
            "chzzk_name": "스트리머",
            "chzzk_image_url": "https://example.com/a.png",
            "channel_id": CHANNEL_ID,
            "channel_name": "알림-채널",
            "guild_id": GUILD_ID,
            "custom_message": "",
            "disable_embed": False,
            "disable_button": False,
            "disable_tag": False,
            "disable_notification": False,
            "index": -1,
        }
        subscription_active.assert_not_called()

    def test_saves_body_options(self, ddb):
        save(
            body={
                "custom_message": "방송 시작!",
                "disable_embed": True,
                "disable_button": True,
                "disable_notification": True,
            }
        )

        noti = get_noti(ddb.table)
        assert noti["custom_message"] == "방송 시작!"
        assert (
            noti["disable_embed"],
            noti["disable_button"],
            noti["disable_notification"],
        ) == (True, True, True)

    @pytest.mark.parametrize(
        "flag",
        ["disable_embed", "disable_button", "disable_tag", "disable_notification"],
    )
    def test_each_flag_is_saved_to_its_own_attribute(self, ddb, flag):
        save(body={flag: True})

        noti = get_noti(ddb.table)
        flags = (
            "disable_embed",
            "disable_button",
            "disable_tag",
            "disable_notification",
        )
        assert {f: noti[f] for f in flags} == {f: f == flag for f in flags}

    @pytest.mark.parametrize("active", [True, False])
    def test_subscriber_options_record_subscription_state(
        self, ddb, subscription_active, active
    ):
        subscription_active.return_value = active
        webhook_url = "https://discord.com/api/webhooks/1/token"

        save(body={"webhook_url": f"  {webhook_url}  ", "embed_color": " #FF0000 "})

        noti = get_noti(ddb.table)
        assert noti["is_subscription_active"] is active
        assert noti["webhook_url"] == webhook_url
        assert noti["embed_color"] == "#FF0000"
        subscription_active.assert_called_once_with(GUILD_ID)

    def test_embed_color_only(self, ddb, subscription_active):
        save(body={"embed_color": "#FF0000"})

        noti = get_noti(ddb.table)
        assert noti["is_subscription_active"] is True
        assert "webhook_url" not in noti

    def test_blank_subscriber_options_are_ignored(self, ddb, subscription_active):
        save(body={"webhook_url": "   ", "embed_color": ""})

        noti = get_noti(ddb.table)
        assert "is_subscription_active" not in noti
        assert "webhook_url" not in noti
        assert "embed_color" not in noti
        subscription_active.assert_not_called()

    def test_duplicate_notification_fails_without_counting(self, ddb):
        put_guild(ddb.table, current_count=0)
        save()

        with pytest.raises(ddb.client.exceptions.TransactionCanceledException):
            save(body={"custom_message": "두 번째"})

        assert get_guild(ddb.table)["current_count"] == 1
        assert get_noti(ddb.table)["custom_message"] == ""

    def test_same_channel_for_other_chzzk_is_separate(self, ddb):
        put_guild(ddb.table)
        save()

        save(chzzk_id="other")

        assert get_guild(ddb.table)["current_count"] == 2

    def test_two_first_notifications_count_two(self, ddb):
        # 새 서버에서 처음 등록이 겹쳐도(둘 다 check_guild_limit에서 GUILD가 없다고 본 경우)
        # GUILD를 덮어쓰지 않고 카운트가 모두 반영된다.
        service.check_guild_limit(GUILD_ID)
        service.check_guild_limit(GUILD_ID)

        save(channel_id="10")
        save(channel_id="11")

        guild = get_guild(ddb.table)
        assert (guild["current_count"], guild["max_limit"]) == (2, 5)

    def test_guild_created_meanwhile_keeps_its_values(self, ddb):
        # check_guild_limit 이후 다른 요청이 GUILD를 만들거나 슬롯을 늘려도 덮어쓰지 않는다.
        service.check_guild_limit(GUILD_ID)
        put_guild(ddb.table, current_count=3, max_limit=250)

        save()

        guild = get_guild(ddb.table)
        assert (guild["current_count"], guild["max_limit"]) == (4, 250)

    def test_partial_guild_item_gets_missing_defaults(self, ddb):
        ddb.table.put_item(
            Item={
                "PK": f"GUILD#{GUILD_ID}",
                "SK": f"GUILD#{GUILD_ID}",
                "current_count": 2,
            }
        )

        save()

        guild = get_guild(ddb.table)
        assert guild == {
            "PK": f"GUILD#{GUILD_ID}",
            "SK": f"GUILD#{GUILD_ID}",
            "type": "GUILD",
            "guild_id": GUILD_ID,
            "max_limit": 5,
            "current_count": 3,
        }

    def test_failed_save_does_not_create_guild(self, ddb):
        ddb.table.put_item(
            Item={
                "PK": f"CHZZK#{CHZZK_ID}",
                "SK": f"NOTI#{CHANNEL_ID}",
                "type": "NOTI",
                "guild_id": GUILD_ID,
            }
        )

        with pytest.raises(ddb.client.exceptions.TransactionCanceledException):
            save()

        assert get_guild(ddb.table) is None

    def test_transaction_error_is_logged(self, mocker, ddb):
        log_error = mocker.patch.object(service.logger, "error")
        put_guild(ddb.table)
        save()

        with pytest.raises(ddb.client.exceptions.TransactionCanceledException):
            save()

        assert '"type": "SAVE_NOTIFICATION_ERROR"' in log_error.call_args.args[0]
