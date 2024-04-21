import asyncio
import aiohttp
from datetime import datetime
import json

import boto3

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

dynamodb = boto3.client('dynamodb')


async def middleware(event, context):
    body = json.loads(event["body"])
    data = body.get("data", {})

    options = data.get("options", [])

    chzzk_id = None
    discord_channel_id = None

    for option in options:
        if option.get("name") == "치지직":
            chzzk_id = option.get("value")
        elif option.get("name") == "채널":
            discord_channel_id = option.get("value")

    channel_data = data \
        .get("resolved", {}) \
        .get("channels", {}) \
        .get(discord_channel_id, {})

    if not chzzk_id:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"치지직 채널 ID를 입력해주세요.",
                "flags": 64  # 64 is the flag for ephemeral messages
            },
        }

    if not discord_channel_id:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"디코 채널을 입력해주세요.",
                "flags": 64  # 64 is the flag for ephemeral messages
            },
        }

    # 채널이 텍스트 채널인지 확인
    if channel_data.get('type') not in [CHANNEL_TYPE.GUILD_TEXT, CHANNEL_TYPE.GUILD_NEWS]:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"텍스트 채널만 등록할 수 있습니다.",
                "flags": 64  # 64 is the flag for ephemeral messages
            },
        }

    async with aiohttp.ClientSession() as session:
        chzzk = await get_chzzk(chzzk_id, session=session)

    # 실제 치지직 채널이 있는지 확인
    if not chzzk:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "embeds": [
                    {
                        "title": f"존재하지 않는 치지직 채널",
                        "description": f"치지직 채널 ID가 `{chzzk_id}`인 채널이 존재하지 않거나 한번도 방송을 키지 않은 채널입니다.\n\n치지직 채널 ID는 치지직 채널의 URL에서 확인할 수 있습니다.\n\n예시: `https://chzzk.naver.com/xyz123456` -> `xyz123456`",
                        "color": 0xF01D15,
                        "footer": {
                            "text": "치직"
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                ],
            },
        }

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='#pk = :pk_val AND #sk = :sk_val',
        ExpressionAttributeNames={
            '#pk': 'PK',
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':pk_val': {'S': f"CHZZK#{chzzk_id}"},
            ':sk_val': {'S': f"CHZZK#{chzzk_id}"}
        }
    )

    # 치지직 채널 정보가 등록되어 있는지 확인
    if not res.get('Items', []):
        res = dynamodb.put_item(
            TableName='chzzk-bot-db',
            Item={
                'PK': {'S': f"CHZZK#{chzzk_id}"},
                'SK': {'S': f"CHZZK#{chzzk_id}"},
                'lastLiveId': {'N': f"{chzzk['liveId']}"},
                'lastLiveTitle': {'S': chzzk['liveTitle']},
                'channelId': {'S': chzzk['channel']['channelId']},
                'channelName': {'S': chzzk['channel']['channelName']},
                'channelImageUrl': {'S': chzzk['channel']['channelImageUrl'] or ""},
                "type": {"S": "CHZZK"},
                "index": {"N": f"{int(chzzk_id, 16) % 6}"}
            }
        )

        # 업로드 실패
        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "embeds": [
                        {
                            "title": f"치지직 채널 정보 등록 실패",
                            "description": f"**{chzzk['channel']['channelName']}**님의 치지직 채널 정보 등록에 실패했습니다. 다시 시도해주세요.",
                            "color": 0xF01D15,
                            "footer": {
                                "text": "치직"
                            },
                            "timestamp": datetime.now().isoformat()
                        },
                    ],
                },
            }

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='#pk = :pk_val AND #sk = :sk_val',
        ExpressionAttributeNames={
            '#pk': 'PK',
            '#sk': 'SK'
        },
        ExpressionAttributeValues={
            ':pk_val': {'S': f"CHZZK#{chzzk_id}"},
            ':sk_val': {'S': f"NOTI#{discord_channel_id}"}
        }
    )

    # 이미 등록된 알림인지 확인
    if res.get('Items', []):
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "embeds": [
                    {
                        "title": f"알림 등록 실패",
                        "description": f"이미 <#{discord_channel_id}>에 등록된 채널(**{chzzk['channel']['channelName']}**)입니다.",
                        "color": 0xF01D15,
                        "footer": {
                            "text": "치직"
                        },
                        "timestamp": datetime.now().isoformat()
                    },
                ],
            },
        }

    res = dynamodb.put_item(
        TableName='chzzk-bot-db',
        Item={
            'PK': {'S': f"CHZZK#{chzzk_id}"},
            'SK': {'S': f"NOTI#{discord_channel_id}"},
            'channel_id': {'S': f"{discord_channel_id}"},
            'channel_name': {'S': channel_data.get('name', '')},
            'guild_id': {'S': channel_data.get('guild_id', '')},
            "custom_message": {'S': ""},
            "type": {"S": "NOTI"},
            "index": {"N": "-1"}
        }
    )

    # 업로드 실패
    if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "embeds": [
                    {
                        "title": f"알림 등록 실패",
                        "description": f"**{chzzk['channel']['channelName']}**님의 방송 알림 등록에 실패했습니다. 다시 시도해주세요.",
                        "color": 0xF01D15,
                        "footer": {
                            "text": "치직"
                        },
                        "url": f"https://chzzk.naver.com/{chzzk_id}",
                        "timestamp": datetime.now().isoformat()
                    },
                ],
            },
        }

    return {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "embeds": [
                {
                    "title": f"알림 등록 완료",
                    "description": f"**{chzzk['channel']['channelName']}**님의 방송 알림을 <#{discord_channel_id}>에 등록했습니다.",
                    "color": 0x02E895,
                    "footer": {
                        "text": "치직"
                    },
                    "url": f"https://chzzk.naver.com/{chzzk_id}",
                    "timestamp": datetime.now().isoformat()
                },
            ],
        }
    }


def handler(event, context):
    return asyncio.run(middleware(event, context))
