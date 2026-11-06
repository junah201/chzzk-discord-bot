import json
from decimal import Decimal

import pytest
from cron.live_check import adapters
from responses import matchers
from shared.discord.utils import DISCORD_API_BASE_URL

CHZZK_ID = "abcdef0123456789abcdef0123456789"
FOLLOWINGS_URL = "https://api.chzzk.naver.com/service/v1/channels/followings"
ERROR_CHANNEL_URL = (
    f"{DISCORD_API_BASE_URL}/channels/"
    f"{adapters.DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID}/messages"
)


@pytest.fixture
def ddb(mocker, dynamodb_table):
    mocker.patch.object(adapters, "dynamodb", dynamodb_table.client)
    mocker.patch.object(adapters, "table", dynamodb_table.table)
    return dynamodb_table


class TestGetFollows:
    @staticmethod
    def following(channel_id, open_live=False):
        return {
            "channel": {"channelId": channel_id},
            "streamer": {"openLive": open_live},
        }

    @staticmethod
    def page(mock_requests, number, followings, total_page):
        mock_requests.get(
            FOLLOWINGS_URL,
            json={"content": {"totalPage": total_page, "followingList": followings}},
            match=[
                matchers.query_param_matcher(
                    {"page": str(number), "size": "505"}, strict_match=False
                ),
                matchers.header_matcher(
                    {"Cookie": "NID_AUT=aut; NID_SES=ses"}, strict_match=False
                ),
            ],
        )

    @pytest.fixture(autouse=True)
    def quiet_logs(self, mocker):
        mocker.patch.object(adapters.logger, "info")

    def test_single_page(self, mock_requests):
        followings = [self.following("a", True), self.following("b")]
        self.page(mock_requests, 0, followings, total_page=1)

        assert adapters.get_follows("aut", "ses", 0) == followings

    def test_collects_every_page(self, mock_requests):
        for number, channel_id in enumerate("abc"):
            self.page(mock_requests, number, [self.following(channel_id)], 3)

        follows = adapters.get_follows("aut", "ses", 0)

        assert [f["channel"]["channelId"] for f in follows] == ["a", "b", "c"]

    def test_no_followings(self, mock_requests):
        self.page(mock_requests, 0, [], total_page=0)

        assert adapters.get_follows("aut", "ses", 0) == []

    def test_error_response_is_reported_to_admin_channel(self, mocker, mock_requests):
        log_error = mocker.patch.object(adapters.logger, "error")
        mock_requests.get(
            FOLLOWINGS_URL, status=401, json={"code": 401, "message": "로그인 필요"}
        )
        mock_requests.post(
            ERROR_CHANNEL_URL,
            json={"id": "1"},
            match=[
                matchers.header_matcher(
                    {"Authorization": f"Bot {adapters.ADMIN_DISCORD_TOKEN}"},
                    strict_match=False,
                )
            ],
        )

        assert adapters.get_follows("aut", "ses", 4) == []

        log = json.loads(log_error.call_args.args[0])
        assert (log["type"], log["status_code"], log["index"]) == (
            "GET_FOLLOWING_ERROR",
            401,
            4,
        )
        [embed] = json.loads(mock_requests.calls[1].request.body)["embeds"]
        assert embed["title"] == "GET_FOLLOWING_ERROR"
        assert {"name": "index", "value": "4"} in embed["fields"]


class TestDynamoDB:
    def put_chzzk(self, table):
        table.put_item(
            Item={
                "PK": f"CHZZK#{CHZZK_ID}",
                "SK": f"CHZZK#{CHZZK_ID}",
                "type": "CHZZK",
                "lastLiveId": 100,
                "lastLiveTitle": "지난 방송",
            }
        )

    def put_noti(self, table, channel_id, chzzk_id=CHZZK_ID):
        table.put_item(
            Item={
                "PK": f"CHZZK#{chzzk_id}",
                "SK": f"NOTI#{channel_id}",
                "type": "NOTI",
                "guild_id": "1",
                "channel_id": channel_id,
            }
        )

    def test_get_naver_session(self, ddb):
        ddb.table.put_item(
            Item={
                "PK": "NAVER#ACCOUNTS",
                "SK": "NAVER#3",
                "NID_AUT": "aut",
                "NID_SES": "ses",
            }
        )
        assert adapters.get_naver_session(3) == ("aut", "ses")

    def test_get_chzzk_item(self, ddb):
        self.put_chzzk(ddb.table)

        item = adapters.get_chzzk_item(CHZZK_ID)

        assert item["lastLiveId"] == 100

    def test_get_chzzk_item_missing_is_logged(self, ddb, mocker):
        log_error = mocker.patch.object(adapters.logger, "error")

        assert adapters.get_chzzk_item("missing") is None
        logged = json.loads(log_error.call_args.args[0])
        assert (logged["type"], logged["chzzk_id"]) == ("GET_DYNAMODB_ERROR", "missing")

    def test_update_last_live(self, ddb):
        self.put_chzzk(ddb.table)

        adapters.update_last_live(CHZZK_ID, {"liveId": 200, "liveTitle": "새 방송"})

        item = adapters.get_chzzk_item(CHZZK_ID)
        assert (item["lastLiveId"], item["lastLiveTitle"]) == (200, "새 방송")

    def test_query_notifications_only_returns_this_channel(self, ddb):
        self.put_chzzk(ddb.table)
        self.put_noti(ddb.table, "10")
        self.put_noti(ddb.table, "11")
        self.put_noti(ddb.table, "20", chzzk_id="other")

        items = adapters.query_notifications(CHZZK_ID)

        assert sorted(i["channel_id"]["S"] for i in items) == ["10", "11"]

    def test_update_notification_sets_given_attributes(self, ddb):
        self.put_noti(ddb.table, "10")
        [item] = adapters.query_notifications(CHZZK_ID)

        adapters.update_notification(
            item,
            {"last_noti_status": {"S": "SUCCESS"}, "noti_fail_count": {"N": "0"}},
        )

        saved = ddb.table.get_item(Key={"PK": f"CHZZK#{CHZZK_ID}", "SK": "NOTI#10"})
        assert saved["Item"]["last_noti_status"] == "SUCCESS"
        assert saved["Item"]["noti_fail_count"] == Decimal(0)
        assert saved["Item"]["guild_id"] == "1"


def test_send_notification_passes_item_fields(mocker):
    send = mocker.patch.object(adapters, "send_notification_message")
    item = {"guild_id": {"S": "1"}, "channel_id": {"S": "10"}}

    adapters.send_notification(item, {"content": "hi"})

    send.assert_called_once_with(
        guild_id="1", channel_id="10", data={"content": "hi"}, notification_item=item
    )


def test_fetch_live_passes_logger(mocker):
    get_chzzk = mocker.patch.object(adapters, "get_chzzk", return_value=None)

    adapters.fetch_live(CHZZK_ID)

    get_chzzk.assert_called_once_with(CHZZK_ID, logger=adapters.logger)
