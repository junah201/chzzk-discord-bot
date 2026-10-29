import json
import logging
import math
import os
import statistics
from collections import defaultdict
from datetime import datetime
from time import perf_counter

import boto3
import requests
from user_agent import generate_user_agent

from shared import send_message

TABLE_NAME = "chzzk-bot-db"
CHZZK_PREFIX = "CHZZK#"
NOTI_PREFIX = "NOTI#"
NAVER_ACCOUNTS_PK = "NAVER#ACCOUNTS"

CHZZK_UNFOLLOW_URL = (
    "https://api.chzzk.naver.com/service/v1/channels/{channel_id}/follow"
)
HTTP_TIMEOUT_SEC = 10
REPORT_FILE_PATH = "/tmp/orphan_cleanup_report.json"

dynamodb = boto3.client("dynamodb")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")
DISCORD_CLEANUP_ORPHAN_CHANNEL_ID = os.getenv("DISCORD_CLEANUP_ORPHAN_CHANNEL_ID")


def parse_dry_run(event) -> bool:
    event = event if isinstance(event, dict) else {}
    value = event.get("dry_run", False)
    if not isinstance(value, bool):
        raise ValueError("'dry_run' must be a boolean")
    return value


def _percentile(sorted_values: list, p: float):
    rank = max(
        0, min(len(sorted_values) - 1, math.ceil(p / 100 * len(sorted_values)) - 1)
    )
    return sorted_values[rank]


def _number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return round(value, 2) if isinstance(value, float) else value


class Metrics:
    def __init__(self):
        self._latencies = defaultdict(list)
        self._counters = defaultdict(float)
        self.stage_ms = {}

    def record(self, op: str, started_at: float):
        self._latencies[op].append((perf_counter() - started_at) * 1000)

    def incr(self, key: str, n=1):
        self._counters[key] += n

    def counters(self) -> dict:
        return {k: _number(v) for k, v in sorted(self._counters.items())}

    def latency_summary(self) -> dict:
        summary = {}
        for op, values in self._latencies.items():
            vals = sorted(values)
            summary[op] = {
                "count": len(vals),
                "avg_ms": round(sum(vals) / len(vals), 2),
                "median_ms": round(statistics.median(vals), 2),
                "p95_ms": round(_percentile(vals, 95), 2),
                "max_ms": round(vals[-1], 2),
            }
        return summary


metrics = Metrics()


def timed_call(name, fn, **kwargs):
    started_at = perf_counter()
    try:
        return fn(**kwargs)
    finally:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        metrics.stage_ms[name] = duration_ms
        logger.info(
            json.dumps(
                {
                    "type": "OPERATION_TIMING",
                    "operation": name,
                    "duration_ms": duration_ms,
                }
            )
        )


def _err(e: Exception) -> str:
    return str(e) or e.__class__.__name__


def scan_table() -> dict:
    """
    테이블을 처음부터 끝까지 순차 Scan 하면서 아래를 한 번에 모은다.
      - 채널 아이템      : PK == SK == "CHZZK#<id>"
      - 알림 아이템      : PK == "CHZZK#<id>", SK 가 "NOTI#" 로 시작 -> 알림이 있는 id 집합
      - 네이버 계정 아이템: PK == "NAVER#ACCOUNTS", SK == "NAVER#<index>"

    Scan 은 한 페이지라도 실패하면 예외를 그대로 올려 전체 작업을 중단한다.
    (일부만 읽은 결과로 고아 판별을 하면 정상 채널이 고아로 보이기 때문)
    """
    channels = {}
    notified_ids = set()
    naver_accounts = {}

    scan_kwargs = {
        "TableName": TABLE_NAME,
        "ProjectionExpression": "#pk, #sk, #ch_id, #ch_name, #idx, #aut, #ses",
        "ExpressionAttributeNames": {
            "#pk": "PK",
            "#sk": "SK",
            "#ch_id": "channelId",
            "#ch_name": "channelName",
            "#idx": "index",
            "#aut": "NID_AUT",
            "#ses": "NID_SES",
        },
        "ReturnConsumedCapacity": "TOTAL",
    }

    start_key = None
    while True:
        if start_key:
            scan_kwargs["ExclusiveStartKey"] = start_key

        started_at = perf_counter()
        response = dynamodb.scan(**scan_kwargs)
        metrics.record("scan_page", started_at)
        metrics.incr("scan_pages")
        metrics.incr("scan_items_scanned", response.get("ScannedCount", 0))
        consumed = response.get("ConsumedCapacity")
        if consumed:
            metrics.incr("scan_consumed_rcu", consumed.get("CapacityUnits", 0))

        for item in response.get("Items", []):
            pk = item.get("PK", {}).get("S", "")
            sk = item.get("SK", {}).get("S", "")

            if pk == NAVER_ACCOUNTS_PK:
                naver_accounts[sk.split("#", 1)[-1]] = {
                    "NID_AUT": item.get("NID_AUT", {}).get("S"),
                    "NID_SES": item.get("NID_SES", {}).get("S"),
                }
            elif pk.startswith(CHZZK_PREFIX):
                chzzk_id = pk[len(CHZZK_PREFIX) :]
                if sk.startswith(NOTI_PREFIX):
                    notified_ids.add(chzzk_id)
                elif sk == pk:
                    channels[chzzk_id] = {
                        "chzzk_id": chzzk_id,
                        "channelId": item.get("channelId", {}).get("S"),
                        "channelName": item.get("channelName", {}).get(
                            "S", "알 수 없음"
                        ),
                        "index": int(item.get("index", {}).get("N", -1)),
                    }

        start_key = response.get("LastEvaluatedKey")
        if not start_key:
            break

    metrics.incr("naver_accounts_count", len(naver_accounts))
    return {
        "channels": channels,
        "notified_ids": notified_ids,
        "naver_accounts": naver_accounts,
    }


def has_notification_consistent(chzzk_id: str) -> bool:
    """
    Scan 은 스냅샷이 아니라서 순회 중에 등록된 알림을 놓칠 수 있다.
    삭제 직전에 강한 일관성으로 한 번 더 확인한다.
    오류가 나면 안전하게 '알림이 있다' 고 간주하여 오삭제를 방지한다.
    """
    started_at = perf_counter()
    try:
        res = dynamodb.query(
            TableName=TABLE_NAME,
            KeyConditionExpression="#pk = :pk_val AND begins_with(#sk, :sk_prefix)",
            ExpressionAttributeNames={"#pk": "PK", "#sk": "SK"},
            ExpressionAttributeValues={
                ":pk_val": {"S": f"{CHZZK_PREFIX}{chzzk_id}"},
                ":sk_prefix": {"S": NOTI_PREFIX},
            },
            Limit=1,
            Select="COUNT",
            ConsistentRead=True,
        )
        metrics.record("recheck_query", started_at)
        return res.get("Count", 0) > 0
    except Exception as e:
        metrics.record("recheck_query", started_at)
        metrics.incr("recheck_error")
        logger.error(
            json.dumps(
                {"type": "CHECK_NOTI_ERROR", "chzzk_id": chzzk_id, "error": str(e)},
                ensure_ascii=False,
            )
        )
        return True


def confirm_orphans(candidate_ids: list) -> list:
    """반환: 확정된 고아 채널 id 목록"""
    confirmed = []
    for chzzk_id in candidate_ids:
        if has_notification_consistent(chzzk_id):
            metrics.incr("recheck_has_notification")  # Scan 이후 알림이 생긴 채널
        else:
            confirmed.append(chzzk_id)
    return confirmed


def unfollow_chzzk_channel(
    channel_id: str, nid_aut: str, nid_ses: str
) -> tuple[bool, str]:
    """치지직 API를 통해 특정 채널 팔로우를 취소합니다."""
    metrics.incr("chzzk_http_calls")
    started_at = perf_counter()
    try:
        res = requests.delete(
            CHZZK_UNFOLLOW_URL.format(channel_id=channel_id),
            headers={
                "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                "Cookie": f"NID_AUT={nid_aut}; NID_SES={nid_ses}",
            },
            timeout=HTTP_TIMEOUT_SEC,
        )
        metrics.record("chzzk_unfollow_http", started_at)
        metrics.incr(f"chzzk_http_status_{res.status_code}")
        if res.status_code == 200:
            return True, ""
        return False, f"HTTP {res.status_code}: {res.text}"
    except Exception as e:
        metrics.record("chzzk_unfollow_http", started_at)
        metrics.incr("chzzk_http_exception")
        return False, _err(e)


def delete_channel_item(chzzk_id: str) -> tuple[str, str | None]:
    started_at = perf_counter()
    try:
        dynamodb.delete_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": f"{CHZZK_PREFIX}{chzzk_id}"},
                "SK": {"S": f"{CHZZK_PREFIX}{chzzk_id}"},
            },
        )
        metrics.record("db_delete_item", started_at)
        metrics.incr("db_delete_success")
        return "SUCCESS", None
    except Exception as e:
        metrics.record("db_delete_item", started_at)
        metrics.incr("db_delete_fail")
        return "FAILED", _err(e)


def get_unfollow_target(channel_info: dict, naver_account_map: dict):
    ch_id = channel_info.get("channelId")
    naver_account = naver_account_map.get(str(channel_info.get("index")))
    if naver_account and ch_id:
        nid_aut = naver_account.get("NID_AUT")
        nid_ses = naver_account.get("NID_SES")
        if nid_aut and nid_ses:
            return ch_id, nid_aut, nid_ses
    return None


def build_report_entry(
    chzzk_id: str,
    channel_info: dict,
    unfollow_status: str,
    unfollow_reason,
    db_status: str,
    db_reason,
) -> dict:
    return {
        "channel_name": channel_info.get("channelName"),
        "channel_id": channel_info.get("channelId"),
        "chzzk_id": chzzk_id,
        "index": channel_info.get("index"),
        "unfollow_status": unfollow_status,
        "unfollow_reason": unfollow_reason,
        "db_delete_status": db_status,
        "db_delete_reason": db_reason,
    }


def process_orphan(
    chzzk_id: str, channel_info: dict, naver_account_map: dict, dry_run: bool
) -> dict:
    """고아 채널 1건에 대해 팔로우 해제 -> DB 삭제를 순서대로 실행"""
    if dry_run:
        metrics.incr("orphan_skipped_dry_run")
        return build_report_entry(
            chzzk_id, channel_info, "DRY_RUN", None, "DRY_RUN", None
        )

    unfollow_success, unfollow_reason = True, None
    target = get_unfollow_target(channel_info, naver_account_map)
    if target:
        unfollow_success, unfollow_reason = unfollow_chzzk_channel(*target)
    else:
        metrics.incr("unfollow_skipped_no_credentials")

    if unfollow_success:
        db_status, db_reason = delete_channel_item(chzzk_id)
    else:
        db_status, db_reason = "SKIPPED", "Unfollow failed"

    return build_report_entry(
        chzzk_id,
        channel_info,
        "SUCCESS" if unfollow_success else "FAILED",
        unfollow_reason,
        db_status,
        db_reason,
    )


def process_all_orphans(
    orphan_ids: list,
    chzzk_channels: dict,
    naver_account_map: dict,
    dry_run: bool,
) -> list:
    """반환: 처리 결과 리포트"""
    report_data = []
    for ch_id in orphan_ids:
        channel_info = chzzk_channels[ch_id]
        try:
            report_data.append(
                process_orphan(ch_id, channel_info, naver_account_map, dry_run)
            )
        except Exception as e:
            metrics.incr("orphan_unexpected_error")
            reason = f"UNEXPECTED: {_err(e)}"
            report_data.append(
                build_report_entry(
                    ch_id, channel_info, "FAILED", reason, "FAILED", reason
                )
            )
    return report_data


def write_report_file(report_data: list) -> str:
    with open(REPORT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=4)
    return REPORT_FILE_PATH


def send_discord_report(
    orphan_count: int,
    deleted_success_count: int,
    deleted_fail_count: int,
    report_file_path: str,
):
    report_description = (
        f"**고아 치지직 채널 자동 정리가 완료되었습니다.**\n\n"
        f"- **탐색된 고아 채널**: {orphan_count}개\n"
        f"- **삭제 성공**: {deleted_success_count}개\n"
        f"- **삭제 실패**: {deleted_fail_count}개\n"
    )
    embeds_data = {
        "embeds": [
            {
                "title": "치지직 고아 채널 정리 리포트",
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
                token=ADMIN_DISCORD_TOKEN,
            )

            metrics.incr(f"discord_status_{res.status_code}")
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
        metrics.incr("discord_exception")
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


def handler(event, context):
    global metrics

    try:
        dry_run = parse_dry_run(event)
    except ValueError as e:
        logger.error(
            json.dumps({"type": "INVALID_EVENT", "error": str(e)}, ensure_ascii=False)
        )
        return {"statusCode": 400, "body": f"Invalid event: {e}"}

    metrics = Metrics()
    handler_started_at = perf_counter()

    # 전체 Scan. 만약 실패하면 아무것도 변경하지 않고 중단
    try:
        scan_result = timed_call("scan_table", scan_table)
    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "SCAN_TABLE_ERROR", "error": _err(e)}, ensure_ascii=False
            )
        )
        return {"statusCode": 500, "body": "Table scan failed. Nothing was changed."}

    chzzk_channels = scan_result["channels"]
    notified_ids = scan_result["notified_ids"]
    naver_account_map = scan_result["naver_accounts"]

    logger.info(
        json.dumps(
            {
                "type": "CHZZK_CHANNELS_SCANNED",
                "channels": len(chzzk_channels),
                "channels_with_notification": len(notified_ids & chzzk_channels.keys()),
                "naver_accounts": len(naver_account_map),
            },
            ensure_ascii=False,
        )
    )

    # 알림이 없는 채널을 후보로 추리고, 삭제 직전 강한 일관성으로 재확인
    candidate_ids = [ch_id for ch_id in chzzk_channels if ch_id not in notified_ids]
    orphan_chzzk_ids = timed_call(
        "confirm_orphans", confirm_orphans, candidate_ids=candidate_ids
    )

    logger.info(
        json.dumps(
            {
                "type": "ORPHAN_CHZZK_CHANNELS",
                "count": len(orphan_chzzk_ids),
                "candidates_from_scan": len(candidate_ids),
                "candidates_detail": candidate_ids,
            },
            ensure_ascii=False,
        )
    )

    report_data = timed_call(
        "process_orphans",
        process_all_orphans,
        orphan_ids=orphan_chzzk_ids,
        chzzk_channels=chzzk_channels,
        naver_account_map=naver_account_map,
        dry_run=dry_run,
    )

    deleted_success_count = sum(
        1 for r in report_data if r["db_delete_status"] == "SUCCESS"
    )
    deleted_fail_count = sum(
        1 for r in report_data if r["db_delete_status"] == "FAILED"
    )

    report_file_path = timed_call(
        "write_report_file", write_report_file, report_data=report_data
    )

    if not dry_run:
        timed_call(
            "send_discord_report",
            send_discord_report,
            orphan_count=len(orphan_chzzk_ids),
            deleted_success_count=deleted_success_count,
            deleted_fail_count=deleted_fail_count,
            report_file_path=report_file_path,
        )

    total_ms = round((perf_counter() - handler_started_at) * 1000, 2)
    summary = {
        "type": "CLEANUP_ORPHAN_SUMMARY",
        "dry_run": dry_run,
        "channels_total": len(chzzk_channels),
        "orphan_candidates": len(candidate_ids),
        "orphans_confirmed": len(orphan_chzzk_ids),
        "orphans_processed": len(report_data),
        "total_ms": total_ms,
        "stage_ms": metrics.stage_ms,
        "counters": metrics.counters(),
        "latency": metrics.latency_summary(),
    }
    logger.info(json.dumps(summary, ensure_ascii=False))

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

    return {
        "statusCode": 200,
        "body": "Weekly cleanup completed successfully.",
        "summary": summary,
    }
