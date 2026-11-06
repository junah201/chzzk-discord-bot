import json
import logging
import traceback
from datetime import UTC, datetime
from time import perf_counter

from cron.live_check import adapters, logic
from shared import middleware
from shared.live_message import build_live_message
from shared.utils import mask_secret

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@middleware(logger)
def handler(event, _context):
    stats = run(logic.parse_account_index(event), now=datetime.now(UTC))
    return {"statusCode": 200, "body": json.dumps(stats.to_dict())}


def _log(level: int, data: dict) -> None:
    logger.log(level, json.dumps(data, ensure_ascii=False))


def run(index: int, now: datetime) -> logic.LiveCheckStats:
    NID_AUT, NID_SES = adapters.get_naver_session(index)
    _log(
        logging.INFO,
        {
            "type": "LIVE_CHECK_START",
            "index": index,
            "NID_AUT": mask_secret(NID_AUT),
            "NID_SES": mask_secret(NID_SES),
        },
    )

    follows = adapters.get_follows(NID_AUT, NID_SES, index)
    live_channels = logic.select_live_channel_ids(follows)
    _log(
        logging.INFO,
        {
            "type": "GET_FOLLOWINGS_SUCCESS",
            "follows_count": len(follows),
            "live_count": len(live_channels),
        },
    )

    stats = logic.LiveCheckStats(
        index=index,
        total_follows_count=len(follows),
        total_live_channels_count=len(live_channels),
    )
    for chzzk_id in live_channels:
        try:
            stats.add(check_channel(chzzk_id, now))
        except Exception as e:
            _log(
                logging.ERROR,
                {
                    "type": "SEND_NOTIFICATION_ERROR",
                    "chzzk_id": chzzk_id,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
            )

    _log(logging.INFO, {"type": "LIVE_CHECK_RESULT", **stats.to_dict()})
    return stats


def check_channel(chzzk_id: str, now: datetime) -> logic.ChannelResult:
    result = logic.ChannelResult()

    item = adapters.get_chzzk_item(chzzk_id)
    if not item:
        return result

    try:
        started_at = perf_counter()
        chzzk = adapters.fetch_live(chzzk_id)
        _log(
            logging.INFO,
            {
                "type": "GET_CHZZK_END",
                "channel_id": chzzk_id,
                "time": perf_counter() - started_at,
                "chzzk": {
                    "liveId": (chzzk or {}).get("liveId", None),
                    "liveTitle": (chzzk or {}).get("liveTitle", None),
                    "status": (chzzk or {}).get("status", None),
                },
            },
        )
    except Exception as e:
        _log(
            logging.ERROR,
            {"type": "GET_CHZZK_ERROR", "channel_id": chzzk_id, "error": str(e)},
        )
        return result

    if not chzzk:
        return result

    if not logic.is_new_live(chzzk, item["lastLiveId"]):
        _log(
            logging.DEBUG,
            {
                "type": "LIVE_NOT_CHANGED",
                "chzzk_id": chzzk_id,
                "liveId": chzzk["liveId"],
            },
        )
        return result

    result.live_start_cnt += 1
    _log(
        logging.INFO,
        {
            "type": "LIVE_START",
            "chzzk_id": chzzk_id,
            "liveId": chzzk["liveId"],
            "liveTitle": chzzk["liveTitle"],
        },
    )
    adapters.update_last_live(chzzk_id, chzzk)

    notifications = adapters.query_notifications(chzzk_id)
    _log(
        logging.INFO,
        {
            "type": "NOTI_QUERY_END",
            "chzzk_id": chzzk_id,
            "noti_count": len(notifications),
        },
    )

    for noti in notifications:
        if not logic.should_notify(noti):
            continue
        is_delivered = _deliver(chzzk_id, chzzk, noti, now)
        if is_delivered:
            result.noti_send_cnt += 1
        else:
            result.noti_fail_cnt += 1

    return result


def _deliver(chzzk_id: str, chzzk: dict, noti: dict, now: datetime) -> bool:
    data = build_live_message(
        chzzk_id,
        chzzk,
        noti,
        content=noti.get("custom_message", {}).get("S", ""),
        now=now,
    )
    res = adapters.send_notification(noti, data)
    delivered = logic.is_delivered(res.status_code)

    log_context = {"chzzk_id": chzzk_id, "discord_channel_id": noti["channel_id"]["S"]}
    if delivered:
        _log(logging.INFO, {"type": "DISCORD_MESSAGE_SEND_SUCCESS", **log_context})
    elif res.status_code == 404:
        _log(logging.ERROR, {"type": "DISCORD_CHANNEL_NOT_FOUND", **log_context})
    else:
        _log(
            logging.ERROR,
            {
                "type": "DISCORD_MESSAGE_SEND_FAIL",
                **log_context,
                "status_code": res.status_code,
                "response": res.text,
            },
        )

    adapters.update_notification(
        noti, logic.delivery_update(res.status_code, noti, chzzk_id, chzzk, now)
    )
    return delivered
