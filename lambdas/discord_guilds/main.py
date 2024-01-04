"""
로그인되어 있는 디스코드 사용자가 관리자인 서버 목록을 반환합니다.
"""

import json

import requests


def middleware(event, context):
    # get authorization header
    headers = event.get("headers", {})
    token = headers.get("Authorization", None)

    if token is None:
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "token is required"}),
        }

    res = requests.get(
        "https://discord.com/api/users/@me/guilds",
        headers={
            "Authorization": token
        }
    )

    if res.status_code != 200:
        return {
            "statusCode": 401,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "token is invalid"}),
        }

    data = res.json()
    print("=== discord response ===")
    print(json.dumps(data))

    # 관리자권한을 가진 서버만 필터링합니다.
    guilds = [
        guild
        for guild in data
        if (guild["permissions"] & 0x8) == 0x8
    ]

    print("=== filtered guilds ===")
    print(json.dumps(guilds))

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(guilds)
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
