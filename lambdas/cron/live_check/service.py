import json
import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from cron.live_check import adapters
from cron.live_check.logic import (
    ChannelResult,
    LiveCheckStats,
    delivery_update,
    is_delivered,
    is_new_live,
    select_live_channel_ids,
    should_notify,
)
from shared import Following
from shared.live_message import build_live_message
from shared.utils import mask_secret

logger = logging.getLogger()


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass
class Deps:
    get_naver_session: Callable[[int], tuple[str, str]]
    get_follows: Callable[[str, str, int], list[Following]]
    get_chzzk_item: Callable[[str], tuple[dict | None, dict | None]]
    fetch_live: Callable[[str], dict | None]
    update_last_live: Callable[[str, dict], None]
    query_notifications: Callable[[str], list[dict]]
    send_notification: Callable[[dict, dict], object]
    update_notification: Callable[[dict, dict], None]
    now: Callable[[], datetime] = _now

    @classmethod
    def default(cls) -> "Deps":
        return cls(
            get_naver_session=adapters.get_naver_session,
            get_follows=adapters.get_follows,
            get_chzzk_item=adapters.get_chzzk_item,
            fetch_live=adapters.fetch_live,
            update_last_live=adapters.update_last_live,
            query_notifications=adapters.query_notifications,
            send_notification=adapters.send_notification,
            update_notification=adapters.update_notification,
        )


def _log(level: int, data: dict) -> None:
    logger.log(level, json.dumps(data, ensure_ascii=False))


def run(index: int, deps: Deps) -> LiveCheckStats:
    NID_AUT, NID_SES = deps.get_naver_session(index)
    _log(
        logging.INFO,
        {
            "type": "LIVE_CHECK_START",
            "index": index,
            "NID_AUT": mask_secret(NID_AUT),
            "NID_SES": mask_secret(NID_SES),
        },
    )

    follows = deps.get_follows(NID_AUT, NID_SES, index)
    live_channels = select_live_channel_ids(follows)
    _log(
        logging.INFO,
        {
            "type": "GET_FOLLOWINGS_SUCCESS",
            "follows_count": len(follows),
            "live_count": len(live_channels),
        },
    )

    stats = LiveCheckStats(
        index=index,
        total_follows_count=len(follows),
        total_live_channels_count=len(live_channels),
    )
    for chzzk_id in live_channels:
        try:
            stats.add(check_channel(chzzk_id, index, deps))
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


def check_channel(chzzk_id: str, index: int, deps: Deps) -> ChannelResult:
    result = ChannelResult()

    item, response_metadata = deps.get_chzzk_item(chzzk_id)
    if not item:
        _log(
            logging.ERROR,
            {
                "type": "GET_DYNAMODB_ERROR",
                "chzzk_id": chzzk_id,
                "index": index,
                "ResponseMetadata": response_metadata,
            },
        )
        return result

    try:
        start_time = deps.now()
        chzzk = deps.fetch_live(chzzk_id)
        _log(
            logging.INFO,
            {
                "type": "GET_CHZZK_END",
                "channel_id": chzzk_id,
                "time": (deps.now() - start_time).total_seconds(),
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

    if not is_new_live(chzzk, item["lastLiveId"]):
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
    deps.update_last_live(chzzk_id, chzzk)

    notifications = deps.query_notifications(chzzk_id)
    _log(
        logging.INFO,
        {
            "type": "NOTI_QUERY_END",
            "chzzk_id": chzzk_id,
            "noti_count": len(notifications),
        },
    )

    for noti in notifications:
        if not should_notify(noti):
            continue
        if _deliver(chzzk_id, chzzk, noti, deps):
            result.noti_send_cnt += 1
        else:
            result.noti_fail_cnt += 1

    return result


def _deliver(chzzk_id: str, chzzk: dict, noti: dict, deps: Deps) -> bool:
    discord_channel_id = noti["channel_id"]["S"]
    data = build_live_message(
        chzzk_id,
        chzzk,
        noti,
        content=noti.get("custom_message", {}).get("S", ""),
        now=deps.now(),
    )
    res = deps.send_notification(noti, data)
    delivered = is_delivered(res.status_code)

    log_context = {"chzzk_id": chzzk_id, "discord_channel_id": discord_channel_id}
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

    deps.update_notification(
        noti, delivery_update(res.status_code, noti, chzzk_id, chzzk, deps.now())
    )
    return delivered
