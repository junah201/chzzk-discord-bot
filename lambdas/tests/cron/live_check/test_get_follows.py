import importlib
import json

import pytest
from responses import matchers
from shared.discord.utils import DISCORD_API_BASE_URL

live_check = importlib.import_module("cron.live_check")

FOLLOWINGS_URL = "https://api.chzzk.naver.com/service/v1/channels/followings"
ERROR_CHANNEL_URL = (
    f"{DISCORD_API_BASE_URL}/channels/"
    f"{live_check.DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID}/messages"
)


def following(channel_id, open_live=False):
    return {"channel": {"channelId": channel_id}, "streamer": {"openLive": open_live}}


def page(mock_requests, number, followings, total_page, status=200):
    mock_requests.get(
        FOLLOWINGS_URL,
        status=status,
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
def quiet_logs(mocker):
    mocker.patch.object(live_check.logger, "info")


def test_single_page(mock_requests):
    page(mock_requests, 0, [following("a", True), following("b")], total_page=1)

    assert live_check.get_follows("aut", "ses", 0) == [
        following("a", True),
        following("b"),
    ]


def test_collects_every_page(mock_requests):
    page(mock_requests, 0, [following("a")], total_page=3)
    page(mock_requests, 1, [following("b")], total_page=3)
    page(mock_requests, 2, [following("c")], total_page=3)

    follows = live_check.get_follows("aut", "ses", 0)

    assert [f["channel"]["channelId"] for f in follows] == ["a", "b", "c"]


def test_no_followings(mock_requests):
    page(mock_requests, 0, [], total_page=0)

    assert live_check.get_follows("aut", "ses", 0) == []


def test_error_response_is_reported_to_admin_channel(mocker, mock_requests):
    log_error = mocker.patch.object(live_check.logger, "error")
    mock_requests.get(
        FOLLOWINGS_URL, status=401, json={"code": 401, "message": "로그인 필요"}
    )
    mock_requests.post(
        ERROR_CHANNEL_URL,
        json={"id": "1"},
        match=[
            matchers.header_matcher(
                {"Authorization": f"Bot {live_check.ADMIN_DISCORD_TOKEN}"},
                strict_match=False,
            )
        ],
    )

    assert live_check.get_follows("aut", "ses", 4) == []

    log = json.loads(log_error.call_args.args[0])
    assert (log["type"], log["status_code"], log["index"]) == (
        "GET_FOLLOWING_ERROR",
        401,
        4,
    )
    [embed] = json.loads(mock_requests.calls[1].request.body)["embeds"]
    assert embed["title"] == "GET_FOLLOWING_ERROR"
    assert {"name": "index", "value": "4"} in embed["fields"]
