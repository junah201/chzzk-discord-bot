import boto3

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    body = event.get("body", {})
    data = body.get("data", {})

    options = data.get("options", [])

    Chzzk_id = None
    discord_channel_id = None

    for option in options:
        if option.get("name") == "치지직":
            Chzzk_id = option.get("value")
        elif option.get("name") == "채널":
            discord_channel_id = option.get("value")

    channel_data = data \
        .get("resolved", {}) \
        .get("channels", {}) \
        .get(discord_channel_id, {})

    if not Chzzk_id:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"치지직 채널 ID를 입력해주세요.",
            },
        }

    if not discord_channel_id:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"디코 채널을 입력해주세요.",
            },
        }

    chzzk = get_chzzk(Chzzk_id)

    # 실제 치지직 채널이 있는지 확인
    if not chzzk:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"존재하지 않는 치지직 채널입니다.",
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
            ':pk_val': {'S': f'CHZZK#{Chzzk_id}'},
            ':sk_val': {'S': f'CHZZK#{Chzzk_id}'}
        }
    )

    # 치지직 채널 정보가 등록되어 있는지 확인
    if not res.get('Items', []):
        res = dynamodb.put_item(
            TableName='chzzk-bot-db',
            Item={
                'PK': {'S': f'CHZZK#{Chzzk_id}'},
                'SK': {'S': f'CHZZK#{Chzzk_id}'},
                'lastLiveId': {'N': f"{chzzk.liveId}"},
                'lastLiveTitle': {'S': chzzk.liveTitle},
                'channelId': {'S': chzzk.channel.channelId},
                'channelName': {'S': chzzk.channel.channelName},
                'channelImageUrl': {'S': chzzk.channel.channelImageUrl},
            }
        )

        # 업로드 실패
        if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {
                "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": {
                    "content": f"치지직 채널 정보 등록에 실패했습니다. 다시 시도해주세요.",
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
            ':pk_val': {'S': f'CHZZK#{Chzzk_id}'},
            ':sk_val': {'S': f'NOTI#{discord_channel_id}'}
        }
    )

    # 이미 등록된 알림인지 확인
    if res.get('Items', []):
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"이미 해당 디코 채널에 등록된 치지직 채널입니다.",
            },
        }

    res = dynamodb.put_item(
        TableName='chzzk-bot-db',
        Item={
            'PK': {'S': f'CHZZK#{Chzzk_id}'},
            'SK': {'S': f'NOTI#{discord_channel_id}'},
            'channel_id': {'S': f'{discord_channel_id}'},
            'channel_name': {'S': channel_data.get('name', '')},
            'guild_id': {'S': channel_data.get('guild_id', '')},
        }
    )

    # 업로드 실패
    if res["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": f"치지직 알림 등록에 실패했습니다. 다시 시도해주세요.",
            },
        }

    return {
        "type": INTERACTION_CALLBACK_TYPE.CHANNEL_MESSAGE_WITH_SOURCE,
        "data": {
            "content": f"치지직 알림 등록에 성공했습니다.",
        }
    }
