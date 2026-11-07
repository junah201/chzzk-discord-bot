import json
from decimal import Decimal

import pytest
from cron.live_check import adapters
from responses import matchers
from shared.discord.utils import DISCORD_API_BASE_URL

CHZZK_ID = "abcdef0123456789abcdef0123456789"
ERROR_CHANNEL_URL = (
    f"{DISCORD_API_BASE_URL}/channels/"
    f"{adapters.DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID}/messages"
)


@pytest.fixture
def ddb(mocker, dynamodb_table):
    mocker.patch.object(adapters, "dynamodb", dynamodb_table.client)
    mocker.patch.object(adapters, "table", dynamodb_table.table)
    return dynamodb_table


class TestFetchLiveStreams:
    @pytest.fixture(autouse=True)
    def quiet_logs(self, mocker):
        mocker.patch.object(adapters.logger, "info")

    def test_returns_following_list(self, mock_requests):
        followings = [{"channel": {"channelId": "a"}, "streamer": {"openLive": True}}]
        mock_requests.get(
            adapters.LIVE_STREAMS_SOURCE_URL,
            json={"code": 200, "content": {"followingList": followings}},
            match=[
                matchers.header_matcher(
                    {"Cookie": "NID_AUT=aut; NID_SES=ses"}, strict_match=False
                ),
            ],
        )

        assert adapters.fetch_live_streams("aut", "ses", 0) == followings

    def test_no_content(self, mock_requests):
        mock_requests.get(
            adapters.LIVE_STREAMS_SOURCE_URL, json={"code": 200, "content": None}
        )

        assert adapters.fetch_live_streams("aut", "ses", 0) == []

    def test_error_response_is_reported_to_admin_channel(self, mocker, mock_requests):
        log_error = mocker.patch.object(adapters.logger, "error")
        mock_requests.get(
            adapters.LIVE_STREAMS_SOURCE_URL, status=401, json={"code": 401}
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

        assert adapters.fetch_live_streams("aut", "ses", 4) == []

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

    def test_get_chzzk_items(self, ddb):
        self.put_chzzk(ddb.table)

        items = adapters.get_chzzk_items([CHZZK_ID])

        assert list(items) == [CHZZK_ID]
        assert items[CHZZK_ID]["lastLiveId"] == 100

    def test_get_chzzk_items_in_chunks_of_100(self, ddb, mocker):
        ids = [f"{i:032x}" for i in range(250)]
        for chzzk_id in ids:
            ddb.table.put_item(
                Item={"PK": f"CHZZK#{chzzk_id}", "SK": f"CHZZK#{chzzk_id}"}
            )
        spy = mocker.spy(ddb.table.meta.client, "batch_get_item")

        items = adapters.get_chzzk_items(ids + ids[:3])

        assert sorted(items) == ids
        sizes = [
            len(c.kwargs["RequestItems"][adapters.TABLE_NAME]["Keys"])
            for c in spy.call_args_list
        ]
        assert sizes == [100, 100, 50]

    def test_get_chzzk_items_missing_is_logged(self, ddb, mocker):
        self.put_chzzk(ddb.table)
        log_error = mocker.patch.object(adapters.logger, "error")

        assert list(adapters.get_chzzk_items([CHZZK_ID, "missing"])) == [CHZZK_ID]
        logged = json.loads(log_error.call_args.args[0])
        assert logged == {"type": "GET_DYNAMODB_ERROR", "chzzk_ids": ["missing"]}

    def test_get_chzzk_items_retries_unprocessed_keys(self, ddb, mocker):
        sleep = mocker.patch.object(adapters.time, "sleep")
        key_b = {"PK": "CHZZK#b", "SK": "CHZZK#b"}
        batch_get = mocker.patch.object(
            ddb.table.meta.client,
            "batch_get_item",
            side_effect=[
                {
                    "Responses": {adapters.TABLE_NAME: [{"PK": "CHZZK#a"}]},
                    "UnprocessedKeys": {adapters.TABLE_NAME: {"Keys": [key_b]}},
                },
                {
                    "Responses": {adapters.TABLE_NAME: [{"PK": "CHZZK#b"}]},
                    "UnprocessedKeys": {},
                },
            ],
        )

        items = adapters.get_chzzk_items(["a", "b"])

        assert sorted(items) == ["a", "b"]
        assert batch_get.call_args_list[1].kwargs["RequestItems"] == {
            adapters.TABLE_NAME: {"Keys": [key_b]}
        }
        sleep.assert_called_once_with(adapters.BATCH_GET_BACKOFF_SEC)

    def test_get_chzzk_items_gives_up_after_max_attempts(self, ddb, mocker):
        mocker.patch.object(adapters.time, "sleep")
        log_error = mocker.patch.object(adapters.logger, "error")
        unprocessed = {
            "Responses": {},
            "UnprocessedKeys": {
                adapters.TABLE_NAME: {"Keys": [{"PK": "CHZZK#a", "SK": "CHZZK#a"}]}
            },
        }
        batch_get = mocker.patch.object(
            ddb.table.meta.client, "batch_get_item", return_value=unprocessed
        )

        assert adapters.get_chzzk_items(["a"]) == {}
        assert batch_get.call_count == adapters.BATCH_GET_MAX_ATTEMPTS
        logged = json.loads(log_error.call_args.args[0])
        assert logged == {"type": "BATCH_GET_UNPROCESSED_KEYS", "chzzk_ids": ["a"]}

    def test_get_chzzk_items_error_only_skips_that_chunk(self, ddb, mocker):
        ids = [f"{i:032x}" for i in range(150)]
        for chzzk_id in ids:
            ddb.table.put_item(
                Item={"PK": f"CHZZK#{chzzk_id}", "SK": f"CHZZK#{chzzk_id}"}
            )
        log_error = mocker.patch.object(adapters.logger, "error")
        client = ddb.table.meta.client
        real_batch_get = client.batch_get_item
        calls = []

        def fail_first_chunk(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                raise RuntimeError("throttled")
            return real_batch_get(**kwargs)

        mocker.patch.object(client, "batch_get_item", side_effect=fail_first_chunk)

        items = adapters.get_chzzk_items(ids)

        assert sorted(items) == ids[100:]
        [logged] = [json.loads(c.args[0]) for c in log_error.call_args_list]
        assert (logged["type"], logged["chzzk_ids"], logged["error"]) == (
            "BATCH_GET_ERROR",
            ids[:100],
            "throttled",
        )

    def test_get_chzzk_items_empty(self, ddb, mocker):
        spy = mocker.spy(ddb.table.meta.client, "batch_get_item")

        assert adapters.get_chzzk_items([]) == {}
        spy.assert_not_called()

    def test_update_last_live(self, ddb):
        self.put_chzzk(ddb.table)

        adapters.update_last_live(CHZZK_ID, {"liveId": 200, "liveTitle": "새 방송"})

        item = adapters.get_chzzk_items([CHZZK_ID])[CHZZK_ID]
        assert (item["lastLiveId"], item["lastLiveTitle"]) == (200, "새 방송")

    def test_update_last_live_without_title(self, ddb):
        self.put_chzzk(ddb.table)

        adapters.update_last_live(CHZZK_ID, {"liveId": 200, "liveTitle": None})

        item = adapters.get_chzzk_items([CHZZK_ID])[CHZZK_ID]
        assert (item["lastLiveId"], item["lastLiveTitle"]) == (200, "")

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
        guild_id="1",
        channel_id="10",
        data={"content": "hi"},
        notification_item=item,
        crosspost=True,
    )
