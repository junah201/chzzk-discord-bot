import aiohttp
import json
import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


async def delete_message(
    channel_id: int,
    message_id: int,
    session: aiohttp.ClientSession,
    token: str = DISCORD_TOKEN
) -> aiohttp.ClientResponse:
    async with session.delete(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
        headers={
            "Authorization": f"Bot {token}",
        }
    ) as res:
        if res.status != 204:
            raise Exception(
                f"Failed to delete message: {res.status} {res.text}")
        return res


async def send_message(
    channel_id: int,
    data: dict,
    session: aiohttp.ClientSession,
    token: str = DISCORD_TOKEN
) -> aiohttp.ClientResponse:
    async with session.post(
        f"https://discord.com/api/v9/channels/{channel_id}/messages",
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    ) as res:
        return res


async def get_channel(
    channel_id: int,
    session: aiohttp.ClientSession,
    token: str = DISCORD_TOKEN,
) -> dict | None:
    async with session.get(
        f"https://discord.com/api/v10/channels/{channel_id}",
        headers={
            "Authorization": f"Bot {token}",
        },
    ) as res:
        if res.status != 200:
            return None
        return await res.json()
