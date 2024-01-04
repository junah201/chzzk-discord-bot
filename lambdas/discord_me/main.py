"""
로그인되어 있는 디스코드 사용자의 정보를 가져옵니다.
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
        "https://discord.com/api/users/@me",
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

    return {
        "statusCode": 200,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        "body": json.dumps(data)
    }


def lambda_handler(event, context):
    print("=== event ===")
    print(json.dumps(event))

    res = middleware(event, context)

    print("=== response ===")
    print(json.dumps(res))

    return res
