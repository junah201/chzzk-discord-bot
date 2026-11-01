import importlib
import json

import pytest
from shared.discord.utils import AdminGuildsResult

discord_guilds = importlib.import_module("api.guilds.discord_guilds")

TOKEN = "Bearer user-token"


def event(headers=None):
    return {"headers": {"Authorization": TOKEN} if headers is None else headers}


def admin_guild(guild_id, **extra):
    return {
        "id": guild_id,
        "name": f"guild-{guild_id}",
        "icon": None,
        "banner": None,
        "owner": False,
        "permissions": "8",
        "features": [],
        "approximate_member_count": 10,
        "approximate_presence_count": 3,
        **extra,
    }


@pytest.fixture
def get_admin_guilds(mocker):
    return mocker.patch.object(discord_guilds, "get_admin_guilds")


@pytest.fixture
def batch_get_item(mocker):
    return mocker.patch.object(
        discord_guilds.dynamodb_client,
        "batch_get_item",
        return_value={"Responses": {"chzzk-bot-db": []}},
    )


def call(evt=None):
    res = discord_guilds.handler(evt or event(), None)
    return res, json.loads(res["body"])


def test_missing_token_is_401(get_admin_guilds):
    res, body = call(event(headers={}))

    assert res["statusCode"] == 401
    assert body["code"] == "UNAUTHORIZED"
    get_admin_guilds.assert_not_called()


def test_requests_admin_guilds_with_counts(get_admin_guilds):
    get_admin_guilds.return_value = AdminGuildsResult([], 200)

    call()

    get_admin_guilds.assert_called_once_with(TOKEN, with_counts=True, retry=2)


def test_rate_limited_is_429(get_admin_guilds, batch_get_item):
    get_admin_guilds.return_value = AdminGuildsResult(None, 429, "RateLimited", 1.5)

    res, body = call()

    assert res["statusCode"] == 429
    assert body["code"] == "RATE_LIMITED"
    assert body["retry_after"] == 1.5
    batch_get_item.assert_not_called()


@pytest.mark.parametrize(
    "status_code",
    [-1, -2, -3, 401, 403, 500],
    ids=["timeout", "connection-error", "invalid-response", "401", "403", "500"],
)
def test_discord_failure_is_502(get_admin_guilds, batch_get_item, status_code):
    get_admin_guilds.return_value = AdminGuildsResult(None, status_code, "error")

    res, body = call()

    assert res["statusCode"] == 502
    assert body["code"] == "DISCORD_API_ERROR"
    batch_get_item.assert_not_called()


def test_no_admin_guilds_returns_empty_list(get_admin_guilds, batch_get_item):
    get_admin_guilds.return_value = AdminGuildsResult([], 200)

    res, body = call()

    assert res["statusCode"] == 200
    assert body == []
    batch_get_item.assert_not_called()


def test_returns_allowed_keys_with_slot_info(get_admin_guilds, batch_get_item):
    get_admin_guilds.return_value = AdminGuildsResult(
        [admin_guild("1"), admin_guild("2")], 200
    )
    batch_get_item.return_value = {
        "Responses": {
            "chzzk-bot-db": [
                {
                    "guild_id": {"S": "1"},
                    "current_count": {"N": "3"},
                    "max_limit": {"N": "10"},
                }
            ]
        }
    }

    res, body = call()

    assert res["statusCode"] == 200
    assert body == [
        {
            "id": "1",
            "name": "guild-1",
            "icon": None,
            "approximate_member_count": 10,
            "current_count": 3,
            "max_limit": 10,
        },
        {
            "id": "2",
            "name": "guild-2",
            "icon": None,
            "approximate_member_count": 10,
            "current_count": 0,
            "max_limit": 5,
        },
    ]
    batch_get_item.assert_called_once_with(
        RequestItems={
            "chzzk-bot-db": {
                "Keys": [
                    {"PK": {"S": "GUILD#1"}, "SK": {"S": "GUILD#1"}},
                    {"PK": {"S": "GUILD#2"}, "SK": {"S": "GUILD#2"}},
                ]
            }
        }
    )


def test_batch_get_item_is_chunked_by_100(get_admin_guilds, batch_get_item):
    get_admin_guilds.return_value = AdminGuildsResult(
        [admin_guild(str(i)) for i in range(150)], 200
    )

    res, body = call()

    assert res["statusCode"] == 200
    assert len(body) == 150
    assert [
        len(c.kwargs["RequestItems"]["chzzk-bot-db"]["Keys"])
        for c in batch_get_item.call_args_list
    ] == [100, 50]
