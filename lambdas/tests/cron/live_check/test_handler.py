import importlib
import json

import pytest

live_check = importlib.import_module("cron.live_check")

NID_AUT = "AUT1" + "x" * 40 + "AUT9"
NID_SES = "SES1" + "y" * 200 + "SES9"
EVENT = {
    "resources": ["arn:aws:events:ap-northeast-2:123:rule/live_check_trigger_for_3"]
}


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(live_check, "dynamodb", dynamodb_table.client)
    mocker.patch.object(live_check, "table", dynamodb_table.table)
    dynamodb_table.table.put_item(
        Item={
            "PK": "NAVER#ACCOUNTS",
            "SK": "NAVER#3",
            "type": "NAVER",
            "NID_AUT": NID_AUT,
            "NID_SES": NID_SES,
        }
    )
    return dynamodb_table


@pytest.fixture
def get_follows(mocker):
    return mocker.patch.object(live_check, "get_follows", return_value=[])


@pytest.fixture
def log_info(mocker):
    return mocker.patch.object(live_check.logger, "info")


def logged(log_mock, log_type):
    for c in log_mock.call_args_list:
        data = json.loads(c.args[0])
        if data.get("type") == log_type:
            return data
    raise AssertionError(f"{log_type} 로그가 없습니다.")


@pytest.mark.usefixtures("log_info")
def test_uses_account_index_from_rule_name(get_follows):
    res = live_check.handler(EVENT, None)

    assert res["statusCode"] == 200
    assert json.loads(res["body"])["index"] == 3
    get_follows.assert_called_once_with(NID_AUT, NID_SES, 3)


@pytest.mark.usefixtures("get_follows")
def test_session_cookies_are_masked_in_logs(log_info):
    live_check.handler(EVENT, None)

    start = logged(log_info, "LIVE_CHECK_START")
    assert start["NID_AUT"] == "AUT1...AUT9"
    assert start["NID_SES"] == "SES1...SES9"
    for c in log_info.call_args_list:
        assert NID_AUT not in c.args[0]
        assert NID_SES not in c.args[0]


@pytest.mark.usefixtures("log_info")
def test_sends_notification_for_live_channels(mocker, get_follows):
    get_follows.return_value = [
        {"channel": {"channelId": "a"}, "streamer": {"openLive": True}},
        {"channel": {"channelId": "b"}, "streamer": {"openLive": False}},
        {"channel": {"channelId": "c"}, "streamer": {"openLive": True}},
    ]
    send_notification = mocker.patch.object(
        live_check, "send_notification", side_effect=[(1, 2, 0), (1, 0, 1)]
    )

    res = live_check.handler(EVENT, None)

    assert [c.args for c in send_notification.call_args_list] == [("a", 3), ("c", 3)]
    assert json.loads(res["body"]) == {
        "index": 3,
        "total_follows_count": 3,
        "total_live_channels_count": 2,
        "total_live_start_cnt": 2,
        "total_noti_send_cnt": 2,
        "total_noti_fail_cnt": 1,
    }


@pytest.mark.usefixtures("log_info")
def test_one_channel_error_does_not_stop_others(mocker, get_follows):
    log_error = mocker.patch.object(live_check.logger, "error")
    get_follows.return_value = [
        {"channel": {"channelId": "a"}, "streamer": {"openLive": True}},
        {"channel": {"channelId": "b"}, "streamer": {"openLive": True}},
    ]
    mocker.patch.object(
        live_check,
        "send_notification",
        side_effect=[RuntimeError("boom"), (1, 1, 0)],
    )

    res = live_check.handler(EVENT, None)

    body = json.loads(res["body"])
    assert (body["total_live_start_cnt"], body["total_noti_send_cnt"]) == (1, 1)
    assert json.loads(log_error.call_args.args[0])["type"] == "SEND_NOTIFICATION_ERROR"
