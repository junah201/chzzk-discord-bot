import requests
import json
import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


def delete_message(channel_id: int, message_id: int):
    res = requests.delete(
        f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
    )
    if res.status_code != 204:
        raise Exception(
            f"Failed to delete message: {res.status_code} {res.text}")


def send_message(channel_id: int, data: dict):
    res = requests.post(
        f"https://discord.com/api/v9/channels/{channel_id}/messages",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )

    return res


def get_channel(channel_id, token=DISCORD_TOKEN) -> dict | None:
    res = requests.get(
        f"https://discord.com/api/v10/channels/{channel_id}",
        headers={
            "Authorization": f"Bot {token}",
        },
    )
    if res.status_code != 200:
        return None

    return res.json()
