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
    if res.status_code != 200:
        raise Exception(
            f"Failed to send message: {res.status_code} {res.text}")
