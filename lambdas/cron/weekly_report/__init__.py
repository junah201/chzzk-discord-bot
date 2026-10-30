import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone

import boto3

from lambdas.shared.discord.utils import send_message

ADMIN_DISCORD_TOKEN = os.environ.get("ADMIN_DISCORD_TOKEN")

LOG_GROUP_PREFIX = "/aws/lambda/"
DISCORD_WEEKLY_REPORT_CHANNEL_ID = os.environ.get("DISCORD_WEEKLY_REPORT_CHANNEL_ID")
DISCORD_WEEKLY_REPORT_ERROR_CHANNEL_ID = os.environ.get(
    "DISCORD_WEEKLY_REPORT_ERROR_CHANNEL_ID", DISCORD_WEEKLY_REPORT_CHANNEL_ID
)

LOG_GROUP_SAVE = "post_notification_v2"
LOG_GROUP_DELETE = "delete_notification_v2"
LOG_GROUP_UPDATE = "update_notification_v2"
LOG_GROUP_LIVE_CHECK = "live_check_v2"
LOG_GROUP_KOREANBOTS = "sync_koreanbots_stats_v2"

QUERY_TIMEOUT_SEC = 240
KST = timezone(timedelta(hours=9))

logger = logging.getLogger()

logs_client = boto3.client("logs")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE_NAME", "chzzk-bot-db"))

REPORT_PK = "REPORT#WEEKLY"


def count_query(log_type: str) -> str:
    return f'filter type = "{log_type}" | stats count(*) as cnt'


LIVE_CHECK_QUERY = """
filter type = "LIVE_CHECK_RESULT"
| stats sum(total_live_start_cnt) as live_start,
        sum(total_noti_send_cnt) as noti_send,
        sum(total_noti_fail_cnt) as noti_fail,
        latest(total_follows_count) as follows
  by `index`
"""

KOREANBOTS_QUERY = """
filter type = "KOREANBOTS_UPDATE_SUCCESS"
| sort @timestamp desc
| limit 1
| fields servers
"""


def get_week_range(event: dict):
    """
    직전 주 월요일 00:00:00 ~ 일요일 23:59:59 (KST) 범위를 반환한다.
    event 에 {"base_date": "YYYY-MM-DD"} 를 넣으면 해당 날짜가 속한 주의
    '직전 주'를 대상으로 한다. (과거 데이터 재생성/테스트용)
    """
    base_date = (event or {}).get("base_date")
    if base_date:
        now = datetime.strptime(base_date, "%Y-%m-%d").replace(tzinfo=KST)
    else:
        now = datetime.now(KST)

    this_monday = (now - timedelta(days=now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start = this_monday - timedelta(days=7)
    end = this_monday - timedelta(seconds=1)
    return start, end


def to_epoch(dt: datetime) -> int:
    return int(dt.timestamp())


def run_queries(specs: dict) -> dict:
    """
    specs: {name: {"log_group", "query", "start", "end"}}
    모든 쿼리를 동시에 시작하고 완료될 때까지 폴링한다.
    반환: {name: [ {field: value, ...}, ... ]}
    """
    pending = {}
    for name, spec in specs.items():
        res = logs_client.start_query(
            logGroupName=f"{LOG_GROUP_PREFIX}{spec['log_group']}",
            startTime=to_epoch(spec["start"]),
            endTime=to_epoch(spec["end"]),
            queryString=spec["query"],
            limit=1000,
        )
        pending[name] = res["queryId"]

    results = {}
    deadline = time.time() + QUERY_TIMEOUT_SEC

    while pending:
        if time.time() > deadline:
            for query_id in pending.values():
                try:
                    logs_client.stop_query(queryId=query_id)
                except Exception:
                    pass
            raise TimeoutError(f"Logs Insights query timeout: {list(pending)}")

        for name, query_id in list(pending.items()):
            res = logs_client.get_query_results(queryId=query_id)
            status = res["status"]

            if status == "Complete":
                results[name] = [
                    {f["field"]: f["value"] for f in row if f["field"] != "@ptr"}
                    for row in res["results"]
                ]
                del pending[name]
            elif status in ("Failed", "Cancelled", "Timeout", "Unknown"):
                raise RuntimeError(f"Logs Insights query {name} {status}")

        if pending:
            time.sleep(1)

    return results


def to_int(value, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def get_count(rows: list) -> int:
    return to_int(rows[0].get("cnt")) if rows else 0


def get_servers(rows: list):
    if not rows or rows[0].get("servers") is None:
        return None
    return to_int(rows[0]["servers"])


def build_report(start: datetime, end: datetime) -> dict:
    prev_start = start - timedelta(days=7)
    prev_end = start - timedelta(seconds=1)

    specs = {
        "save": {
            "log_group": LOG_GROUP_SAVE,
            "query": count_query("SAVE_NOTIFICATION_SUCCESS"),
            "start": start,
            "end": end,
        },
        "delete": {
            "log_group": LOG_GROUP_DELETE,
            "query": count_query("DELETE_NOTIFICATION_SUCCESS"),
            "start": start,
            "end": end,
        },
        "update": {
            "log_group": LOG_GROUP_UPDATE,
            "query": count_query("UPDATE_NOTIFICATION_SUCCESS"),
            "start": start,
            "end": end,
        },
        "live_check": {
            "log_group": LOG_GROUP_LIVE_CHECK,
            "query": LIVE_CHECK_QUERY,
            "start": start,
            "end": end,
        },
        "servers": {
            "log_group": LOG_GROUP_KOREANBOTS,
            "query": KOREANBOTS_QUERY,
            "start": start,
            "end": end,
        },
        # 전주 대비 증감 계산용
        "servers_prev": {
            "log_group": LOG_GROUP_KOREANBOTS,
            "query": KOREANBOTS_QUERY,
            "start": prev_start,
            "end": prev_end,
        },
    }

    results = run_queries(specs)

    # 라이브 체크: index 별 집계 + 전체 합계
    index_stats = []
    for row in results["live_check"]:
        index_stats.append(
            {
                "index": to_int(row.get("index")),
                "live_start": to_int(row.get("live_start")),
                "noti_send": to_int(row.get("noti_send")),
                "noti_fail": to_int(row.get("noti_fail")),
                "follows": to_int(row.get("follows")),
            }
        )
    index_stats.sort(key=lambda x: x["index"])

    return {
        "period": {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
        },
        "notification": {
            "saved": get_count(results["save"]),
            "deleted": get_count(results["delete"]),
            "updated": get_count(results["update"]),
        },
        "live_check": {
            "total_live_start": sum(s["live_start"] for s in index_stats),
            "total_noti_send": sum(s["noti_send"] for s in index_stats),
            "total_noti_fail": sum(s["noti_fail"] for s in index_stats),
            "by_index": index_stats,
        },
        "servers": {
            "current": get_servers(results["servers"]),
            "previous": get_servers(results["servers_prev"]),
        },
    }


def format_servers(servers: dict) -> str:
    current, previous = servers["current"], servers["previous"]
    if current is None:
        return "`데이터 없음`"
    if previous is None:
        return f"`{current:,}`개"
    diff = current - previous
    sign = "+" if diff > 0 else ""
    return f"`{current:,}`개 (전주 대비 `{sign}{diff:,}`)"


def format_index_stats(by_index: list) -> str:
    if not by_index:
        return "`데이터 없음`"

    lines = [f"`#{s['index']}` 팔로우 `{s['follows']:,}`명" for s in by_index]
    value = "\n".join(lines)
    if len(value) > 1000:  # 디스코드 embed field 길이 제한(1024)
        value = value[:1000] + "\n..."
    return value


def save_report(report: dict):
    """
    주간 리포트를 DynamoDB 에 저장한다. (백오피스 조회용)
    같은 주를 다시 실행하면 동일한 키로 덮어쓴다.
    """
    table.put_item(
        Item={
            "PK": REPORT_PK,
            "SK": report["period"]["start"],
            "type": "WEEKLY_REPORT",
            "period_start": report["period"]["start"],
            "period_end": report["period"]["end"],
            "notification": report["notification"],
            "live_check": report["live_check"],
            "servers": report["servers"],
        }
    )


def send_report(report: dict):
    if not DISCORD_WEEKLY_REPORT_CHANNEL_ID:
        logger.warning("DISCORD_WEEKLY_REPORT_CHANNEL_ID is not set. skip sending.")
        return

    noti = report["notification"]
    live = report["live_check"]
    period = report["period"]

    send_message(
        channel_id=DISCORD_WEEKLY_REPORT_CHANNEL_ID,
        data={
            "embeds": [
                {
                    "title": "주간 리포트",
                    "description": f"{period['start']} (월) ~ {period['end']} (일)",
                    "color": 0x5865F2,
                    "fields": [
                        {
                            "name": "알림 설정 변경",
                            "value": (
                                f"등록: `{noti['saved']:,}`건\n"
                                f"삭제: `{noti['deleted']:,}`건\n"
                                f"수정: `{noti['updated']:,}`건"
                            ),
                            "inline": False,
                        },
                        {
                            "name": "라이브 알림 통계",
                            "value": (
                                f"라이브 시작 채널: `{live['total_live_start']:,}`개\n"
                                f"발송된 알림: `{live['total_noti_send']:,}`건\n"
                                f"실패한 알림: `{live['total_noti_fail']:,}`건"
                            ),
                            "inline": False,
                        },
                        {
                            "name": "Index 별 팔로우 수 (마지막 기록)",
                            "value": format_index_stats(live["by_index"]),
                            "inline": False,
                        },
                        {
                            "name": "디스코드 서버 수",
                            "value": format_servers(report["servers"]),
                            "inline": False,
                        },
                    ],
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        },
        token=ADMIN_DISCORD_TOKEN,
    )


def send_error_alert(error: Exception):
    if not DISCORD_WEEKLY_REPORT_ERROR_CHANNEL_ID:
        return

    try:
        send_message(
            channel_id=DISCORD_WEEKLY_REPORT_ERROR_CHANNEL_ID,
            data={
                "embeds": [
                    {
                        "title": "WEEKLY_REPORT_ERROR",
                        "description": "주간 리포트 생성에 실패했습니다.",
                        "color": 0xFF0000,
                        "fields": [
                            {
                                "name": "Error",
                                "value": f"`{str(error)[:500]}`",
                                "inline": False,
                            }
                        ],
                    }
                ]
            },
            token=ADMIN_DISCORD_TOKEN,
        )
    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "WEEKLY_REPORT_ERROR_ALERT_FAILED", "error": str(e)},
                ensure_ascii=False,
            )
        )


def handler(event, context):
    try:
        start, end = get_week_range(event)
        report = build_report(start, end)
    except Exception as e:
        logger.error(
            json.dumps(
                {"type": "WEEKLY_REPORT_BUILD_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        send_error_alert(e)
        return {"statusCode": 500, "error": "Failed to build weekly report"}

    logger.info(
        json.dumps(
            {"type": "WEEKLY_REPORT_RESULT", **report},
            ensure_ascii=False,
        )
    )

    failed = []

    try:
        save_report(report)
    except Exception as e:
        failed.append("save")
        logger.error(
            json.dumps(
                {"type": "WEEKLY_REPORT_SAVE_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )
        send_error_alert(e)

    try:
        send_report(report)
    except Exception as e:
        failed.append("send")
        logger.error(
            json.dumps(
                {"type": "WEEKLY_REPORT_SEND_ERROR", "error": str(e)},
                ensure_ascii=False,
            )
        )

    if failed:
        return {"statusCode": 500, "error": f"Failed: {', '.join(failed)}"}

    return {"statusCode": 200, "report": report}
