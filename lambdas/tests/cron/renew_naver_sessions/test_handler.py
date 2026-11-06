import importlib
import json

import pytest
import requests
import responses

renew_naver_sessions = importlib.import_module("cron.renew_naver_sessions")

USER_STATUS_URL = "https://comm-api.game.naver.com/nng_main/v1/user/getUserStatus"
NID_AUT = "AUT1" + "a" * 40 + "AUT9"
NID_SES = "SES1" + "b" * 200 + "SES9"
NEW_NID_SES = "NEW1" + "c" * 200 + "NEW9"
SECRETS = (NID_AUT, NID_SES, NEW_NID_SES)


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(renew_naver_sessions, "dynamodb", dynamodb_table.client)
    return dynamodb_table


@pytest.fixture(autouse=True)
def sleep(mocker):
    return mocker.patch.object(renew_naver_sessions.time, "sleep")


@pytest.fixture
def send_message(mocker):
    return mocker.patch.object(
        renew_naver_sessions,
        "send_message",
        return_value=mocker.Mock(status_code=200, text="{}"),
    )


@pytest.fixture
def logs(mocker):
    return {
        level: mocker.patch.object(renew_naver_sessions.logger, level)
        for level in ("info", "error")
    }


def put_account(table, index=0, nid_aut=NID_AUT, nid_ses=NID_SES):
    item = {
        "PK": "NAVER#ACCOUNTS",
        "SK": f"NAVER#{index}",
        "type": "NAVER",
        "NID_AUT": nid_aut,
        "NID_SES": nid_ses,
    }
    table.put_item(Item={k: v for k, v in item.items() if v is not None})


def get_account(table, index=0):
    return table.get_item(Key={"PK": "NAVER#ACCOUNTS", "SK": f"NAVER#{index}"})["Item"]


def add_user_status(rsps, new_nid_ses=NEW_NID_SES):
    headers = {}
    if new_nid_ses:
        headers["Set-Cookie"] = f"NID_SES={new_nid_ses}; Path=/; Domain=.naver.com"
    rsps.add(responses.GET, USER_STATUS_URL, json={"code": 200}, headers=headers)


def logged(log_mock, log_type):
    for c in log_mock.call_args_list:
        data = json.loads(c.args[0])
        if data.get("type") == log_type:
            return data
    raise AssertionError(f"{log_type} 로그가 없습니다.")


def assert_no_secret_logged(logs):
    for log_mock in logs.values():
        for c in log_mock.call_args_list:
            for secret in SECRETS:
                assert secret not in c.args[0]


class TestRenewed:
    def test_updates_session_and_masks_logs(self, ddb, mock_requests, logs):
        put_account(ddb.table)
        add_user_status(mock_requests)

        result = renew_naver_sessions.handler({}, None)

        assert get_account(ddb.table)["NID_SES"] == NEW_NID_SES
        assert get_account(ddb.table)["NID_AUT"] == NID_AUT
        expected = {
            "SK": "NAVER#0",
            "NID_AUT": "AUT1...AUT9",
            "ORIGINAL_NID_SES": "SES1...SES9",
            "NEW_NID_SES": "NEW1...NEW9",
        }
        assert result == [expected]
        assert logged(logs["info"], "NAVER_SESSION_RENEW")["result"] == [expected]
        assert_no_secret_logged(logs)

    def test_sends_current_cookies(self, ddb, mock_requests, logs):
        put_account(ddb.table)
        add_user_status(mock_requests)

        renew_naver_sessions.handler({}, None)

        request = mock_requests.calls[0].request
        assert request.headers["Cookie"] == f"NID_AUT={NID_AUT}; NID_SES={NID_SES}"
        assert (
            request.req_kwargs["timeout"]
            == renew_naver_sessions.NAVER_REQUEST_TIMEOUT_SEC
        )

    def test_renews_every_account_in_order(self, ddb, mock_requests, logs, sleep):
        put_account(ddb.table, index=1)
        put_account(ddb.table, index=0)
        add_user_status(mock_requests, "NEW_SESSION_FOR_FIRST_ACCOUNT")
        add_user_status(mock_requests, "NEW_SESSION_FOR_SECOND_ACCOUNT")

        result = renew_naver_sessions.handler({}, None)

        assert [r["SK"] for r in result] == ["NAVER#0", "NAVER#1"]
        assert get_account(ddb.table, 0)["NID_SES"] == "NEW_SESSION_FOR_FIRST_ACCOUNT"
        assert get_account(ddb.table, 1)["NID_SES"] == "NEW_SESSION_FOR_SECOND_ACCOUNT"
        assert sleep.call_count == 2


class TestRenewFailed:
    def test_keeps_session_and_alerts_with_masked_cookies(
        self, ddb, mock_requests, logs, send_message
    ):
        put_account(ddb.table)
        add_user_status(mock_requests, new_nid_ses=None)

        result = renew_naver_sessions.handler({}, None)

        assert get_account(ddb.table)["NID_SES"] == NID_SES
        assert result == [
            {
                "SK": "NAVER#0",
                "NID_AUT": "AUT1...AUT9",
                "ORIGINAL_NID_SES": "SES1...SES9",
                "NEW_NID_SES": "error",
            }
        ]
        assert logged(logs["error"], "NAVER_SESSION_RENEW_ERROR")["PK"] == (
            "NAVER#ACCOUNTS"
        )
        assert logged(logs["error"], "NAVER_SESSION_RENEW_EXPIRED") == {
            "type": "NAVER_SESSION_RENEW_EXPIRED",
            "SK": "NAVER#0",
            "NID_AUT": "AUT1...AUT9",
            "NID_SES": "SES1...SES9",
        }
        assert_no_secret_logged(logs)

        send_message.assert_called_once()
        kwargs = send_message.call_args.kwargs
        assert kwargs["token"] == renew_naver_sessions.ADMIN_DISCORD_TOKEN
        fields = {f["name"]: f["value"] for f in kwargs["data"]["embeds"][0]["fields"]}
        assert fields == {
            "SK": "`NAVER#0`",
            "NID_AUT": "`AUT1...AUT9`",
            "NID_SES": "`SES1...SES9`",
        }

    def test_missing_cookie_values_do_not_crash(
        self, ddb, mock_requests, logs, send_message
    ):
        put_account(ddb.table, nid_aut=None, nid_ses=None)
        add_user_status(mock_requests, new_nid_ses=None)

        result = renew_naver_sessions.handler({}, None)

        assert result[0]["NID_AUT"] is None
        assert result[0]["ORIGINAL_NID_SES"] is None
        fields = {
            f["name"]: f["value"]
            for f in send_message.call_args.kwargs["data"]["embeds"][0]["fields"]
        }
        assert (fields["NID_AUT"], fields["NID_SES"]) == ("`None`", "`None`")

    def test_expired_cookie_is_not_saved(self, ddb, mock_requests, logs, send_message):
        put_account(ddb.table)
        add_user_status(mock_requests, new_nid_ses="expired")

        result = renew_naver_sessions.handler({}, None)

        assert get_account(ddb.table)["NID_SES"] == NID_SES
        assert result[0]["NEW_NID_SES"] == "expired"
        assert logged(logs["error"], "NAVER_SESSION_RENEW_EXPIRED")["SK"] == "NAVER#0"
        send_message.assert_called_once()

    def test_one_failed_account_does_not_block_others(
        self, ddb, mock_requests, logs, send_message
    ):
        put_account(ddb.table, index=0)
        put_account(ddb.table, index=1)
        add_user_status(mock_requests, new_nid_ses=None)
        add_user_status(mock_requests, "NEW_SESSION_FOR_SECOND_ACCOUNT")

        result = renew_naver_sessions.handler({}, None)

        assert [r["NEW_NID_SES"] for r in result] == ["error", "NEW_...OUNT"]
        assert get_account(ddb.table, 0)["NID_SES"] == NID_SES
        assert get_account(ddb.table, 1)["NID_SES"] == "NEW_SESSION_FOR_SECOND_ACCOUNT"
        send_message.assert_called_once()

    @pytest.mark.parametrize(
        "error",
        [
            requests.exceptions.ReadTimeout("read timed out"),
            requests.exceptions.ConnectionError("connection refused"),
        ],
        ids=["timeout", "connection-error"],
    )
    def test_network_error_does_not_block_others(
        self, ddb, mock_requests, logs, send_message, error
    ):
        put_account(ddb.table, index=0)
        put_account(ddb.table, index=1)
        mock_requests.add(responses.GET, USER_STATUS_URL, body=error)
        add_user_status(mock_requests, "NEW_SESSION_FOR_SECOND_ACCOUNT")

        result = renew_naver_sessions.handler({}, None)

        assert [r["NEW_NID_SES"] for r in result] == ["error", "NEW_...OUNT"]
        assert get_account(ddb.table, 0)["NID_SES"] == NID_SES
        assert get_account(ddb.table, 1)["NID_SES"] == "NEW_SESSION_FOR_SECOND_ACCOUNT"
        log = logged(logs["error"], "NAVER_SESSION_RENEW_REQUEST_ERROR")
        assert log == {
            "type": "NAVER_SESSION_RENEW_REQUEST_ERROR",
            "SK": "NAVER#0",
            "error": str(error),
        }
        send_message.assert_called_once()
        assert_no_secret_logged(logs)
