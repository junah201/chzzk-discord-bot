import importlib
import json

import pytest
from responses import matchers
from shared.discord.utils import DISCORD_API_BASE_URL

sync_koreanbots_stats = importlib.import_module("cron.sync_koreanbots_stats")

APPLICATION_URL = f"{DISCORD_API_BASE_URL}/applications/@me"
STATS_URL = "https://koreanbots.dev/api/v2/bots/1234/stats"


@pytest.fixture(autouse=True)
def quiet_logs(mocker):
    mocker.patch.object(sync_koreanbots_stats.logger, "info")
    return mocker.patch.object(sync_koreanbots_stats.logger, "error")


@pytest.fixture
def alert(mocker):
    return mocker.patch.object(sync_koreanbots_stats, "send_message")


def add_application(mock_requests, **data):
    mock_requests.get(APPLICATION_URL, json={"id": "1234", **data})


@pytest.mark.parametrize(
    ("data", "servers"),
    [
        ({"bot_approximate_guild_count": 321, "approximate_guild_count": 1}, 321),
        ({"approximate_guild_count": 123}, 123),
        ({}, 0),
    ],
    ids=["bot-count", "fallback-count", "no-count"],
)
def test_posts_server_count(mock_requests, data, servers):
    add_application(mock_requests, **data)
    mock_requests.post(
        STATS_URL,
        json={"code": 200},
        match=[
            matchers.json_params_matcher({"servers": servers}),
            matchers.header_matcher(
                {"Authorization": sync_koreanbots_stats.KOREANBOTS_TOKEN},
                strict_match=False,
            ),
        ],
    )

    result = sync_koreanbots_stats.handler({}, None)

    assert result == {
        "type": "KOREANBOTS_UPDATE_SUCCESS",
        "bot_id": "1234",
        "servers": servers,
        "response": {"code": 200},
    }


def test_discord_failure_skips_koreanbots(mock_requests, alert, quiet_logs):
    mock_requests.get(APPLICATION_URL, status=401, json={"message": "401"})

    result = sync_koreanbots_stats.handler({}, None)

    assert result["statusCode"] == 500
    assert json.loads(quiet_logs.call_args.args[0])["type"] == (
        "DISCORD_GET_GUILD_COUNT_ERROR"
    )
    alert.assert_not_called()


def test_koreanbots_failure_alerts_admin(mock_requests, alert):
    add_application(mock_requests, bot_approximate_guild_count=321)
    mock_requests.post(STATS_URL, status=500, body="server error")

    result = sync_koreanbots_stats.handler({}, None)

    assert result["statusCode"] == 500
    alert.assert_called_once()
    kwargs = alert.call_args.kwargs
    assert kwargs["token"] == sync_koreanbots_stats.ADMIN_DISCORD_TOKEN
    fields = {f["name"]: f["value"] for f in kwargs["data"]["embeds"][0]["fields"]}
    assert fields["Servers"] == "`321`"
    assert fields["Response Text"] == "```server error```"
