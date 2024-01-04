"""
Discord OAuth2 Redirect
"""

import os
import json
from datetime import datetime

import requests

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")


def middleware(event, context):
    body = json.loads(event.get("body", "{}"))
    code = body.get("code", None)

    if code is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "code is required"}),
        }

    res = requests.post(
        url="https://discord.com/api/v10/oauth2/token",
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data={
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': "http://localhost:3000/login",
            'scope': 'identify, email, guilds'
        }
    )

    if res.status_code != 200:
        return {
            "statusCode": 401,
            "headers": {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            "body": json.dumps({"message": "code is invalid"}),
        }

    data = res.json()
    print("=== token response ===")
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
