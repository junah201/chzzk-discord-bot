"""
특정 시간마다 DynamoDB에 저장된 채널 정보들을 조회하여 채널이 라이브 중일 경우 디스코드 알림을 보냅니다.
"""

import asyncio
import json
from datetime import datetime

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import boto3

dynamodb = boto3.client('dynamodb')


async def send_notice_message(
    chzzk: ChzzkLive,
    noti: dict,
    index: str,
    session: aiohttp.ClientSession
) -> bool:
    """
    해당 디스코드 채널로 방송 알림 메시지를 전송하고, 성공 여부를 반환합니다.
    """

    res = await send_message(
        channel_id=noti["channel_id"]["S"],
        data={
            "content": noti.get("custom_message", {}).get("S", ""),
            "embeds": [
                {
                    "title": f"{chzzk['liveTitle']}",
                    "description": f"{chzzk['channel']['channelName']} 님이 방송을 시작했습니다.",
                    "color": 0x02E895,
                    "fields": [
                        {
                            "name": '카테고리',
                            "value": chzzk['liveCategoryValue']
                        }
                    ],
                    "image": {
                        "url": (chzzk['liveImageUrl'] or chzzk['channel']['channelImageUrl'] or "").replace("_{type}", "_1080"),
                    },
                    "author": {
                        "name": f"{chzzk['channel']['channelName']}",
                        "url": f"https://chzzk.naver.com/live/{chzzk['channel']['channelId']}",
                        "icon_url": chzzk['channel']['channelImageUrl'] or "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na"
                    },
                    "footer": {
                        "text": f"치직 ({index})"
                    },
                    "url": f"https://chzzk.naver.com/live/{chzzk['channel']['channelId']}",
                    "timestamp": datetime.now().isoformat()
                },
            ],
            "components": [
                {
                    "type": COMPONENT_TYPE.ACTION_ROW,
                    "components": [
                        {
                            "type": COMPONENT_TYPE.BUTTON,
                            "label": "바로가기",
                            "style": BUTTON_STYLE.LINK,
                            "url": f"https://chzzk.naver.com/live/{chzzk['channel']['channelId']}"
                        }
                    ]
                },
            ],
        },
        session=session
    )

    # 채널이 존재하지 않는 경우
    if res.status == 404:
        print(
            f"channel not found, NOTI#{noti['channel_id']['S']} CHZZK#{chzzk['channel']['channelId']}, index: {index}"
        )
        dynamodb.delete_item(
            TableName='chzzk-bot-db',
            Key={
                'PK': noti.get('PK'),
                'SK': noti.get('SK')
            }
        )
        return False

    # 메시지 전송에 실패한 경우
    if res.status != 200:
        msg = f"send message fail {res.status}, NOTI#{noti['channel_id']['S']} CHZZK#{chzzk['channel']['channelId']}, index: {index}"
        try:
            msg += f"\n{await res.json()}"
        except:
            try:
                msg += f"\n{await res.text()}"
            except Exception as e:
                msg += f"\n{e}"
        print(msg)
        return False

    # 성공
    print(
        f"send message success, NOTI#{noti['channel_id']['S']} CHZZK#{chzzk['channel']['channelId']}, index: {index}")
    return True


async def check_live(item: dict, index: str, session: aiohttp.ClientSession):
    chzzk_channel_id = item["PK"]["S"].split("#")[1]
    last_live_id = item["lastLiveId"]["N"]

    chzzk = await get_chzzk(
        chzzk_channel_id,
        session=session
    )
    if not chzzk:
        return (1, 0, 0, 0)

    if str(chzzk['liveId']) == str(last_live_id):
        return (1, 0, 0, 0)

    if chzzk['status'] != "OPEN":
        return (1, 0, 0, 0)

    dynamodb.update_item(
        TableName='chzzk-bot-db',
        Key={
            'PK': item.get('PK'),
            'SK': item.get('SK')
        },
        UpdateExpression='SET lastLiveId = :live_id, lastLiveTitle = :live_title',
        ExpressionAttributeValues={
            ':live_id': {'N': f"{chzzk['liveId']}"},
            ':live_title': {'S': chzzk['liveTitle']}
        }
    )

    print(
        f"LIVE_START {chzzk['channel']['channelName']}, {chzzk['liveId']}, {chzzk['liveTitle']}, index: {index}")

    all_noti = dynamodb.query(
        TableName='chzzk-bot-db',
        KeyConditionExpression='PK = :pk_val AND begins_with(SK, :sk_val)',
        ExpressionAttributeValues={
            ':pk_val': {'S': f"CHZZK#{chzzk_channel_id}"},
            ':sk_val': {'S': 'NOTI#'}
        }
    )

    tmp = await asyncio.gather(
        *[
            send_notice_message(
                chzzk,
                noti,
                index=index,
                session=session
            ) for noti in all_noti["Items"]
        ]
    )

    # 총 채널 개수, 라이브를 킨 채널 개수, 알림 전송 성공 개수, 알림 전송 실패 개수
    return (1, 1, tmp.count(True), tmp.count(False))


async def middleware(event, context):
    index = int(event.get("resources", [])[0][-1])
    """
    트리거마다 처리하는 데이터가 다르게 분산화합니다.
    """

    res = dynamodb.query(
        TableName='chzzk-bot-db',
        IndexName='GSI-index',
        KeyConditionExpression='#PK = :index_val',
        ExpressionAttributeNames={
            '#PK': 'index'
        },
        ExpressionAttributeValues={
            ':index_val': {'N': f"{index}"}
        }
    )

    async with aiohttp.ClientSession() as session:
        tmp = await asyncio.gather(
            *[
                check_live(
                    item,
                    index,
                    session
                ) for item in res["Items"]
            ]
        )

    result = {
        "index": index,
        "total_channel_count": sum([i[0] for i in tmp]),
        "live_channel_count": sum([i[1] for i in tmp]),
        "total_send_count": sum([i[2] for i in tmp]),
        "fail_send_count": sum([i[3] for i in tmp]),
    }

    return result


def lambda_handler(event, context):
    res = asyncio.run(middleware(event, context))

    print("=== res ===")
    print(json.dumps(res))

    return res
