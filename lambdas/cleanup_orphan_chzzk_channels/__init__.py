import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError
from user_agent import generate_user_agent

from shared import send_message

aws_config = Config(max_pool_connections=50)

dynamodb = boto3.client("dynamodb", config=aws_config)
table = boto3.resource("dynamodb").Table("chzzk-bot-db")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DISCORD_CLEANUP_ORPHAN_CHANNEL_ID = os.getenv("DISCORD_CLEANUP_ORPHAN_CHANNEL_ID")


def unfollow_chzzk_channel(
    channel_id: str, nid_aut: str, nid_ses: str
) -> tuple[bool, str]:
    """치지직 API를 통해 특정 채널 팔로우를 취소합니다."""
    try:
        res = requests.delete(
            f"https://api.chzzk.naver.com/service/v1/channels/{channel_id}/follow",
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={nid_aut}; NID_SES={nid_ses}",
            },
            timeout=10,
        )
        if res.status_code == 200:
            return True, ""
        else:
            return False, f"HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return False, str(e)


def check_channel_has_notification(chzzk_id: str) -> tuple[str, bool]:
    """개별 채널의 알림 존재 여부를 확인하는 함수 (병렬 처리용)"""
    try:
        noti_res = dynamodb.query(
            TableName="chzzk-bot-db",
            KeyConditionExpression="#pk = :pk_val AND begins_with(#sk, :sk_prefix)",
            ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
            ExpressionAttributeValues={
                ":pk_val": {"S": f"CHZZK#{chzzk_id}"},
                ":sk_prefix": {"S": "NOTI#"},
            },
            Limit=1,
            Select="COUNT",
        )
        has_noti = noti_res.get("Count", 0) > 0
        return chzzk_id, has_noti
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "CHECK_NOTI_ERROR",
                    "chzzk_id": chzzk_id,
                    "error": str(e),
                },
                ensure_ascii=False,
            )
        )
        # 에러 난 경우 안전하게 알림이 있다고 간주하여 오삭제 방지
        return chzzk_id, True


def handler(event, context):
    chzzk_channels = {}

    query_kwargs = {
        "TableName": "chzzk-bot-db",
        "IndexName": "GSI-type",
        "KeyConditionExpression": "#type_key = :type_val",
        "ExpressionAttributeNames": {"#type_key": "type"},
        "ExpressionAttributeValues": {":type_val": {"S": "CHZZK"}},
    }

    done = False
    start_key = None

    while not done:
        if start_key:
            query_kwargs["ExclusiveStartKey"] = start_key

        response = dynamodb.query(**query_kwargs)

        for item in response.get("Items", []):
            chzzk_id = item.get("chzzk_id", {}).get("S") or item.get("PK", {}).get(
                "S", ""
            ).replace("CHZZK#", "")
            chzzk_channels[chzzk_id] = {
                "chzzk_id": chzzk_id,
                "channelId": item.get("channelId", {}).get("S"),
                "channelName": item.get("channelName", {}).get("S", "알 수 없음"),
                "index": int(item.get("index", {}).get("N", -1)),
            }

        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            done = True
        else:
            query_kwargs["ExclusiveStartKey"] = start_key

    logger.info(
        json.dumps(
            {"type": "GSI_CHZZK_CHANNELS", "count": len(chzzk_channels)},
            ensure_ascii=False,
        )
    )

    orphan_chzzk_ids = []

    chzzk_ids = list(chzzk_channels.keys())
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {
            executor.submit(check_channel_has_notification, ch_id): ch_id
            for ch_id in chzzk_ids
        }

        for future in as_completed(futures):
            ch_id, has_noti = future.result()
            if not has_noti:
                orphan_chzzk_ids.append(ch_id)

    logger.info(
        json.dumps(
            {"type": "ORPHAN_CHZZK_CHANNELS", "count": len(orphan_chzzk_ids)},
            ensure_ascii=False,
        )
    )

    res = table.query(
        IndexName="GSI-type",
        KeyConditionExpression="#type_key = :type_val",
        ExpressionAttributeNames={"#type_key": "type"},
        ExpressionAttributeValues={":type_val": "NAVER"},
    )
    naver_accounts = res.get("Items", [])
    naver_account_map = {item["PK"].split("#")[1]: item for item in naver_accounts}

    deleted_success_count = 0
    deleted_fail_count = 0
    json_report_data = []

    # 고아 채널 팔로우 해제 및 DB 삭제
    for chzzk_id in orphan_chzzk_ids:
        channel_info = chzzk_channels[chzzk_id]
        channel_name = channel_info.get("channelName")
        ch_id = channel_info.get("channelId")
        index = channel_info.get("index")

        naver_account = naver_account_map.get(str(index))
        unfollow_success = True
        unfollow_reason = None
        if naver_account and ch_id:
            nid_aut = naver_account.get("NID_AUT")
            nid_ses = naver_account.get("NID_SES")
            if nid_aut and nid_ses:
                unfollow_success, unfollow_reason = unfollow_chzzk_channel(
                    ch_id, nid_aut, nid_ses
                )

        item_status = "SUCCESS"
        fail_reason = None

        try:
            dynamodb.delete_item(
                TableName="chzzk-bot-db",
                Key={
                    "PK": {"S": f"CHZZK#{chzzk_id}"},
                    "SK": {"S": f"CHZZK#{chzzk_id}"},
                },
            )
            deleted_success_count += 1
        except ClientError as e:
            item_status = "FAILED"
            fail_reason = str(e)
            deleted_fail_count += 1

        json_report_data.append(
            {
                "channel_name": channel_name,
                "channel_id": ch_id,
                "chzzk_id": chzzk_id,
                "index": index,
                "unfollow_status": "SUCCESS" if unfollow_success else "FAILED",
                "unfollow_reason": unfollow_reason,
                "db_delete_status": item_status,
                "db_delete_reason": fail_reason,
            }
        )

    # 4. /tmp 디렉토리에 JSON 리포트 파일 생성
    report_file_path = "/tmp/orphan_cleanup_report.json"
    with open(report_file_path, "w", encoding="utf-8") as f:
        json.dump(json_report_data, f, ensure_ascii=False, indent=4)

    # 5. 디스코드 전송
    report_description = (
        f"**고아 치지직 채널 주간 자동 정리가 완료되었습니다.**\n\n"
        f"- **탐색된 고아 채널**: {len(orphan_chzzk_ids)}개\n"
        f"- **삭제 성공**: {deleted_success_count}개\n"
        f"- **삭제 실패**: {deleted_fail_count}개\n"
    )

    embeds_data = {
        "embeds": [
            {
                "title": "치지직 고아 채널 주간 리포트",
                "description": report_description,
                "color": 0x3498DB,
                "timestamp": datetime.now().isoformat(),
            }
        ],
    }

    try:
        with open(report_file_path, "rb") as f:
            files_param = {
                "file": ("orphan_cleanup_report.json", f, "application/json")
            }

            res = send_message(
                channel_id=int(DISCORD_CLEANUP_ORPHAN_CHANNEL_ID),
                data=embeds_data,
                files=files_param,
            )

            if res.status_code not in (200, 201):
                logger.error(
                    json.dumps(
                        {
                            "type": "DISCORD_MESSAGE_SEND_ERROR",
                            "error": f"Failed to send Discord file message: {res.status_code} {res.text}",
                            "channel_id": DISCORD_CLEANUP_ORPHAN_CHANNEL_ID,
                        },
                        ensure_ascii=False,
                    )
                )
    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "type": "DISCORD_MESSAGE_SEND_ERROR",
                    "error": str(e),
                    "channel_id": DISCORD_CLEANUP_ORPHAN_CHANNEL_ID,
                },
                ensure_ascii=False,
            )
        )

    logger.info(
        json.dumps(
            {
                "type": "CLEANUP_ORPHAN_CHZZK_CHANNELS_COMPLETED",
                "total_orphan_channels": len(orphan_chzzk_ids),
                "deleted_success_count": deleted_success_count,
                "deleted_fail_count": deleted_fail_count,
            },
            ensure_ascii=False,
        )
    )
    return {"statusCode": 200, "body": "Weekly cleanup completed successfully."}
