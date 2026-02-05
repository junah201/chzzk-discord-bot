import json
import logging
import os

import requests

from shared import middleware

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")


@middleware(logger)
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    code = body.get("code", None)

    if code is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "code is required"}),
        }

    headers = event.get("headers", {})
    origin = headers.get("origin") or headers.get("Origin") or ""

    if "localhost" in origin:
        redirect_uri = "http://localhost:3000/login/callback"
        scope = "identify, email, guilds, guilds.members.read"
        env_label = "Localhost"
    elif "dev.chzzk.junah.dev" in origin:
        redirect_uri = "https://dev.chzzk.junah.dev/login/callback"
        scope = "identify, email, guilds, guilds.members.read"
        env_label = "Dev"
    else:
        redirect_uri = "https://chzzk.junah.dev/login"
        scope = "identify, email, guilds"
        env_label = "Production"

    logger.info(
        f"[{env_label}] Request detected. Origin: {origin}, Using URI: {redirect_uri}"
    )

    res = requests.post(
        url="https://discord.com/api/v10/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "scope": scope,
        },
    )

    if res.status_code != 200:
        logger.error(
            json.dumps(
                {
                    "type": "INVALID_CODE",
                    "status_code": res.status_code,
                    "response": res.text,
                }
            )
        )
        return {
            "statusCode": 401,
            "body": json.dumps({"message": "code is invalid"}),
        }

    data = res.json()

    return {"statusCode": 200, "body": json.dumps(data)}
