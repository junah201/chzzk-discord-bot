"""
특정 ID의 디스코드 서버의 채널 목록을 가져옵니다.
만약 해당 서버가 존재하지 않거나 접근할 수 없는 경우 404를 반환합니다.
"""

import os
import json

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *


import requests

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


def middleware(event, context):
    # get authorization header
    headers = event.get("headers", {})

    guild_id = event.get("pathParameters", {}).get("guild_id", None)

    res = requests.get(
        f"https://discord.com/api/v10/guilds/{guild_id}/channels",
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}"
        }
    )

    # 해당 서버가 존재하지 않거나 접근할 수 없는 경우
    if res.status_code == 404:
        return {
            "statusCode": 404,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "guild not found"}),
        }

    data = res.json()
    print("=== discord response ===")
    print(res.status_code)
    print(json.dumps(data))

    if res.status_code == 403:
        return {
            "statusCode": 403,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "you don't have permission"}),
        }

    if res.status_code == 401:
        return {
            "statusCode": 401,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "token is invalid"}),
        }

    if res.status_code != 200:
        return {
            "statusCode": 400,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "unknown error"}),
        }

    # 채팅 채널 목록을 필터링합니다. (채널이 텍스트 채널 혹은 공지 채널이여야 합니다.)
    channels = [
        channel
        for channel in data
        if channel["type"] in [CHANNEL_TYPE.GUILD_TEXT, CHANNEL_TYPE.GUILD_NEWS]
    ]

    print("=== filtered channels ===")
    print(json.dumps(channels))

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(channels)
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
