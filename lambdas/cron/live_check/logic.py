from dataclasses import dataclass, fields
from datetime import datetime

from shared import Following

SUCCESS_STATUS_CODES = (200, 204)


@dataclass
class ChannelResult:
    live_start_cnt: int = 0
    noti_send_cnt: int = 0
    noti_fail_cnt: int = 0


@dataclass
class LiveCheckStats:
    index: int
    total_follows_count: int = 0
    total_live_channels_count: int = 0
    total_live_start_cnt: int = 0
    total_noti_send_cnt: int = 0
    total_noti_fail_cnt: int = 0

    def add(self, result: ChannelResult) -> None:
        self.total_live_start_cnt += result.live_start_cnt
        self.total_noti_send_cnt += result.noti_send_cnt
        self.total_noti_fail_cnt += result.noti_fail_cnt

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}


def parse_account_index(event: dict) -> int:
    """EventBridge Scheduler가 넘겨준 입력({"index": N})에서 네이버 계정 번호를 꺼냅니다."""
    return int(event["index"])


def select_live_channel_ids(follows: list[Following]) -> list[str]:
    return [f["channel"]["channelId"] for f in follows if f["streamer"]["openLive"]]


def is_new_live(chzzk: dict, last_live_id) -> bool:
    return str(chzzk["liveId"]) != str(last_live_id)


def should_notify(notification_item: dict) -> bool:
    return not notification_item.get("disable_notification", {"BOOL": False})["BOOL"]


def is_delivered(status_code: int) -> bool:
    return status_code in SUCCESS_STATUS_CODES


def delivery_update(
    status_code: int,
    notification_item: dict,
    chzzk_id: str,
    chzzk: dict,
    now: datetime,
) -> dict:
    """전송 결과를 NOTI 아이템에 기록할 속성(DynamoDB client 형식)을 만듭니다."""
    if is_delivered(status_code):
        status = "SUCCESS"
        fail_count = 0
    else:
        status = f"FAIL_{status_code}"
        fail_count = int(notification_item.get("noti_fail_count", {"N": "0"})["N"]) + 1

    return {
        "last_noti_status": {"S": status},
        "last_noti_at": {"S": now.isoformat()},
        "noti_fail_count": {"N": str(fail_count)},
        "chzzk_name": {"S": chzzk["channel"]["channelName"]},
        "chzzk_image_url": {"S": chzzk["channel"]["channelImageUrl"] or ""},
        "chzzk_id": {"S": f"{chzzk_id}"},
    }
