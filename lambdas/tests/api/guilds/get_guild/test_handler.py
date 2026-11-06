import importlib
import json

import pytest
import requests
from shared.discord.utils import DISCORD_API_BASE_URL

get_guild = importlib.import_module("api.guilds.get_guild")

pytestmark = pytest.mark.usefixtures("as_admin")

EVENT = {
    "headers": {"Authorization": "Bearer user-token"},
    "pathParameters": {"guild_id": "1"},
}


@pytest.fixture
def session_get(mocker):
    return mocker.patch.object(get_guild.session, "get")


@pytest.fixture
def ddb(mocker, dynamodb_table):
    mocker.patch.object(get_guild, "table", dynamodb_table.table)
    return dynamodb_table


def call():
    res = get_guild.handler(EVENT, None)
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
    log_error = mocker.patch.object(get_guild.logger, "error")
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


def discord_guild(mocker, session_get):
    session_get.return_value = mocker.Mock(status_code=200, text="{}")
    session_get.return_value.json.return_value = {
        "id": "1",
        "name": "서버",
        "icon": None,
        "description": "설명",
        "approximate_member_count": 10,
        "owner_id": "999",
    }


def test_returns_guild_with_slot_info(mocker, session_get, ddb):
    discord_guild(mocker, session_get)
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
    assert session_get.call_args.args == (f"{DISCORD_API_BASE_URL}/guilds/1",)
    assert session_get.call_args.kwargs["params"] == {"with_counts": "true"}


@pytest.mark.usefixtures("ddb")
def test_guild_without_item_gets_default_slots(mocker, session_get):
    discord_guild(mocker, session_get)

    _, body = call()

    assert (body["current_count"], body["max_limit"]) == (0, 5)
