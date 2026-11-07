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
    started_at = perf_counter()
    NID_AUT, NID_SES = adapters.get_naver_session(index)
    _log(
        logging.INFO,
        {"type": "GET_NAVER_SESSION_END", "time": perf_counter() - started_at},
    )
    _log(
        logging.INFO,
        {
            "type": "LIVE_CHECK_START",
            "index": index,
            "NID_AUT": mask_secret(NID_AUT),
            "NID_SES": mask_secret(NID_SES),
        },
    )

    started_at = perf_counter()
    follows = adapters.fetch_live_streams(NID_AUT, NID_SES, index)
    live_streams = {f["channel"]["channelId"]: f for f in follows}
    _log(
        logging.INFO,
        {
            "type": "FETCH_LIVE_STREAMS_END",
            "live_count": len(live_streams),
            "time": perf_counter() - started_at,
        },
    )

    started_at = perf_counter()
    items = adapters.get_chzzk_items(list(live_streams))
    _log(
        logging.INFO,
        {
            "type": "GET_CHZZK_ITEMS_END",
            "item_count": len(items),
            "time": perf_counter() - started_at,
        },
    )

    stats = logic.LiveCheckStats(
        index=index,
        total_live_channels_count=len(live_streams),
    )
    started_at = perf_counter()
    for chzzk_id, following in live_streams.items():
        try:
            stats.add(check_channel(chzzk_id, items.get(chzzk_id), following, now))
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

    _log(
        logging.INFO,
        {"type": "CHECK_CHANNELS_END", "time": perf_counter() - started_at},
    )
    _log(logging.INFO, {"type": "LIVE_CHECK_RESULT", **stats.to_dict()})
    return stats


def check_channel(
    chzzk_id: str, item: dict | None, following: dict, now: datetime
) -> logic.ChannelResult:
    result = logic.ChannelResult()

    if not item:
        return result

    chzzk = logic.live_from_following(following)
    if not chzzk:
        _log(logging.ERROR, {"type": "LIVE_INFO_MISSING", "chzzk_id": chzzk_id})
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
    started_at = perf_counter()
    adapters.update_last_live(chzzk_id, chzzk)
    notifications = adapters.query_notifications(chzzk_id)
    _log(
        logging.INFO,
        {
            "type": "UPDATE_AND_QUERY_END",
            "chzzk_id": chzzk_id,
            "time": perf_counter() - started_at,
        },
    )
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
        started_at = perf_counter()
        is_delivered = _deliver(chzzk_id, chzzk, noti, now)
        _log(
            logging.INFO,
            {
                "type": "DELIVER_END",
                "chzzk_id": chzzk_id,
                "discord_channel_id": noti["channel_id"]["S"],
                "time": perf_counter() - started_at,
            },
        )
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

    attrs = logic.delivery_update(res.status_code, noti, chzzk_id, chzzk, now)
    adapters.update_notification(noti, attrs)
    if "disable_notification" in attrs:
        _log(
            logging.WARNING,
            {
                "type": "NOTIFICATION_AUTO_DISABLED",
                **log_context,
                "guild_id": noti["guild_id"]["S"],
                "status_code": res.status_code,
                "noti_fail_count": int(attrs["noti_fail_count"]["N"]),
            },
        )
    return delivered
