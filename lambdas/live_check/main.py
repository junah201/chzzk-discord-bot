"""
특정 시간마다 DynamoDB에 저장된 채널 정보들을 조회하여 채널이 라이브 중일 경우 디스코드 알림을 보냅니다.
"""

import json
from datetime import datetime

try:
    from common import *
except ImportError:
    # for local test
    from layers.common.python.common import *

import boto3

dynamodb = boto3.client('dynamodb')


def middleware(event, context):
    index = int(event.get("resources", [])[0][-1])
    """
    트리거마다 처리하는 데이터가 다르게 분산화합니다.
    """

    result = {
        "total_channel_count": 0,
        "live_channel_count": 0,
        "total_send_count": 0,
        "fail_send_count": 0,
    }

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

    result["total_channel_count"] = res["Count"]

    for item in res["Items"]:
        channel_id = item["PK"]["S"].split("#")[1]
        last_live_id = item["lastLiveId"]["N"]

        chzzk = get_chzzk(channel_id)

        if not chzzk:
            continue

        if str(chzzk['liveId']) == str(last_live_id):
            continue

        if chzzk['status'] != "OPEN":
            continue

        result["live_channel_count"] += 1

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
            f"LIVE_START {chzzk['channel']['channelName']}, {chzzk['liveId']}, {chzzk['liveTitle']}, {index=}")

        res = dynamodb.query(
            TableName='chzzk-bot-db',
            KeyConditionExpression='PK = :pk_val AND begins_with(SK, :sk_val)',
            ExpressionAttributeValues={
                ':pk_val': {'S': f"CHZZK#{channel_id}"},
                ':sk_val': {'S': 'NOTI#'}
            }
        )

        for noti in res["Items"]:
            discord_channel_id = noti["channel_id"]["S"]

            data = {
                "content": noti.get("custom_message", {}).get("S", ""),
            }
            if not noti.get("disable_embed", {"BOOL": False})["BOOL"]:
                data["embeds"] = [
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
                            "url": f"https://chzzk.naver.com/live/{channel_id}",
                            "icon_url": chzzk['channel']['channelImageUrl'] or "https://ssl.pstatic.net/cmstatic/nng/img/img_anonymous_square_gray_opacity2x.png?type=f120_120_na"
                        },
                        "footer": {
                            "text": "치직"
                        },
                        "url": f"https://chzzk.naver.com/live/{channel_id}",
                        "timestamp": datetime.now().isoformat()
                    },
                ]
            if not noti.get("disable_button", {"BOOL": False})["BOOL"]:
                data["components"] = [
                    {
                        "type": COMPONENT_TYPE.ACTION_ROW,
                        "components": [
                            {
                                "type": COMPONENT_TYPE.BUTTON,
                                "label": "바로가기",
                                "style": BUTTON_STYLE.LINK,
                                "url": f"https://chzzk.naver.com/live/{channel_id}"
                            }
                        ]
                    },
                ]

            res = send_message(
                channel_id=discord_channel_id,
                data=data
            )

            # 채널이 존재하지 않는 경우
            if res.status_code == 404:
                print("channel not found")
                dynamodb.delete_item(
                    TableName='chzzk-bot-db',
                    Key={
                        'PK': noti.get('PK'),
                        'SK': noti.get('SK')
                    }
                )
                result["fail_send_count"] += 1
                continue

            # 메시지 전송에 실패한 경우
            if res.status_code != 200:
                print("send message fail", res.status_code)
                dynamodb.update_item(
                    TableName='chzzk-bot-db',
                    Key={
                        'PK': noti.get('PK'),
                        'SK': noti.get('SK')
                    },
                    UpdateExpression='SET last_noti_status = :last_noti_status, last_noti_at = :last_noti_at, noti_fail_count = :noti_fail_count',
                    ExpressionAttributeValues={
                        ':last_noti_status': {'S': f"FAIL_{res.status_code}"},
                        ':last_noti_at': {'S': datetime.now().isoformat()},
                        ':noti_fail_count': {'N': str(int(noti.get("noti_fail_count", {"N": "0"})["N"]) + 1)}
                    }
                )
                try:
                    print(res.json())
                except:
                    try:
                        print(res.text)
                    except:
                        print("unknown error")
                result["fail_send_count"] += 1
                continue

            # 성공
            print("send message success")
            result["total_send_count"] += 1
            dynamodb.update_item(
                TableName='chzzk-bot-db',
                Key={
                    'PK': noti.get('PK'),
                    'SK': noti.get('SK')
                },
                UpdateExpression='SET last_noti_status = :last_noti_status, last_noti_at = :last_noti_at, noti_fail_count = :noti_fail_count',
                ExpressionAttributeValues={
                    ':last_noti_status': {'S': f"SUCCESS"},
                    ':last_noti_at': {'S': datetime.now().isoformat()},
                    ':noti_fail_count': {'N': "0"}
                }
            )

    return result


def lambda_handler(event, context):
    res = middleware(event, context)

    print("=== res ===")
    print(json.dumps(res))

    return res
