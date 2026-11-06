import importlib
import json

import pytest
import requests
from shared.discord import CHANNEL_TYPE
from shared.discord.utils import DISCORD_API_BASE_URL

list_guild_channels = importlib.import_module("api.guilds.list_guild_channels")

pytestmark = pytest.mark.usefixtures("as_admin")

EVENT = {
    "headers": {"Authorization": "Bearer user-token"},
    "pathParameters": {"guild_id": "1"},
}


@pytest.fixture
def session_get(mocker):
    return mocker.patch.object(list_guild_channels.session, "get")


def call():
    res = list_guild_channels.handler(EVENT, None)
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
    mocker.patch.object(list_guild_channels.logger, "error")
    session_get.side_effect = error

    res, body = call()

    assert res["statusCode"] == 502
    assert body["code"] == "DISCORD_API_ERROR"


@pytest.mark.parametrize(
    ("status", "expected_status", "code"),
    [
        (404, 404, "SERVER_NOT_FOUND"),
        (403, 404, "BOT_NOT_JOINED"),
        # 봇 토큰 문제는 유저 로그인과 무관하므로 서버 측 오류로 응답한다.
        (401, 502, "DISCORD_API_ERROR"),
        (500, 502, "DISCORD_API_ERROR"),
    ],
)
def test_discord_error_status(mocker, session_get, status, expected_status, code):
    session_get.return_value = mocker.Mock(status_code=status, text="error")

    res, body = call()

    assert res["statusCode"] == expected_status
    assert body["code"] == code


def test_returns_text_and_news_channels_only(mocker, session_get):
    channels = [
        {"id": "1", "type": CHANNEL_TYPE.GUILD_TEXT},
        {"id": "2", "type": CHANNEL_TYPE.GUILD_VOICE},
        {"id": "3", "type": CHANNEL_TYPE.GUILD_NEWS},
        {"id": "4", "type": CHANNEL_TYPE.GUILD_CATEGORY},
    ]
    session_get.return_value = mocker.Mock(status_code=200, text="[]")
    session_get.return_value.json.return_value = channels

    res, body = call()

    assert res["statusCode"] == 200
    assert [c["id"] for c in body] == ["1", "3"]
    assert session_get.call_args.args == (f"{DISCORD_API_BASE_URL}/guilds/1/channels",)


def test_no_text_channels_returns_empty_list(mocker, session_get):
    session_get.return_value = mocker.Mock(status_code=200, text="[]")
    session_get.return_value.json.return_value = [
        {"id": "2", "type": CHANNEL_TYPE.GUILD_VOICE}
    ]

    res, body = call()

    assert body == []
