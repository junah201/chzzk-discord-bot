import importlib
import json

import pytest
import requests
from shared.discord.utils import AdminCheckResult

discord_guild_by_id = importlib.import_module("api.guilds.discord_guild_by_id")
middleware_module = importlib.import_module("shared.middleware")

EVENT = {
    "headers": {"Authorization": "Bearer user-token"},
    "pathParameters": {"guild_id": "1"},
}


@pytest.fixture(autouse=True)
def admin(mocker):
    return mocker.patch.object(
        middleware_module, "is_admin", return_value=AdminCheckResult(True, 200)
    )


@pytest.fixture
def session_get(mocker):
    return mocker.patch.object(discord_guild_by_id.session, "get")


@pytest.fixture
def ddb(mocker, dynamodb_table):
    mocker.patch.object(discord_guild_by_id, "table", dynamodb_table.table)
    return dynamodb_table


def call():
    res = discord_guild_by_id.handler(EVENT, None)
    return res, json.loads(res["body"])


@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.ConnectionError("refused"),
        requests.exceptions.ReadTimeout("read timed out"),
    ],
    ids=["connection-error", "timeout"],
)
def test_network_failure_is_502(mocker, session_get, error):
    log_error = mocker.patch.object(discord_guild_by_id.logger, "error")
    session_get.side_effect = error

    res, body = call()

    assert res["statusCode"] == 502
    assert body["code"] == "DISCORD_API_ERROR"
    logged = [json.loads(c.args[0]) for c in log_error.call_args_list]
    assert logged[0]["type"] == "DISCORD_CONNECTION_FAILURE"


@pytest.mark.parametrize(
    ("status", "expected_status", "code"),
    [
        (404, 404, "SERVER_NOT_FOUND"),
        (403, 404, "BOT_NOT_JOINED"),
        (500, 502, "DISCORD_API_ERROR"),
    ],
)
def test_discord_error_status(mocker, session_get, status, expected_status, code):
    session_get.return_value = mocker.Mock(status_code=status, text="error")

    res, body = call()

    assert res["statusCode"] == expected_status
    assert body["code"] == code


def test_returns_guild_with_slot_info(mocker, session_get, ddb):
    session_get.return_value = mocker.Mock(status_code=200, text="{}")
    session_get.return_value.json.return_value = {
        "id": "1",
        "name": "서버",
        "icon": None,
        "description": "설명",
        "approximate_member_count": 10,
        "owner_id": "999",
    }
    ddb.table.put_item(
        Item={
            "PK": "GUILD#1",
            "SK": "GUILD#1",
            "type": "GUILD",
            "guild_id": "1",
            "current_count": 2,
            "max_limit": 10,
        }
    )

    res, body = call()

    assert res["statusCode"] == 200
    assert body == {
        "id": "1",
        "name": "서버",
        "icon": None,
        "description": "설명",
        "approximate_member_count": 10,
        "current_count": 2,
        "max_limit": 10,
    }
