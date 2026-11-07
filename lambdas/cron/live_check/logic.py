from dataclasses import dataclass, fields
from datetime import datetime

from shared import ChzzkLive, Following
from shared.discord.utils import NETWORK_ERROR_STATUS_CODE

SUCCESS_STATUS_CODES = (200, 204)
MAX_NOTI_FAIL_COUNT = 3


@dataclass
class ChannelResult:
    live_start_cnt: int = 0
    noti_send_cnt: int = 0
    noti_fail_cnt: int = 0


@dataclass
class LiveCheckStats:
    index: int
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


def live_from_following(following: Following) -> ChzzkLive | None:
    """라이브 팔로우 목록 항목을 live-detail과 같은 모양(liveInfo + channel)으로 바꿉니다."""
    live_info = following.get("liveInfo")
    if not live_info or live_info.get("liveId") is None:
        return None
    live = {**live_info, "channel": following["channel"]}
    if live.get("adult"):
        live["liveImageUrl"] = None
    return live


def is_new_live(chzzk: ChzzkLive, last_live_id) -> bool:
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
    prev_fail_count = int(notification_item.get("noti_fail_count", {"N": "0"})["N"])
    # 599는 응답을 못 받은 경우라 실제로는 전달됐을 수 있어 자동 끄기 횟수에 세지 않는다.
    counts_as_failure = status_code != NETWORK_ERROR_STATUS_CODE
    if is_delivered(status_code):
        status = "SUCCESS"
        fail_count = 0
    else:
        status = f"FAIL_{status_code}"
        fail_count = prev_fail_count + 1 if counts_as_failure else prev_fail_count

    attrs = {
        "last_noti_status": {"S": status},
        "last_noti_at": {"S": now.isoformat()},
        "noti_fail_count": {"N": str(fail_count)},
        "chzzk_name": {"S": chzzk["channel"]["channelName"]},
        "chzzk_image_url": {"S": chzzk["channel"]["channelImageUrl"] or ""},
        "chzzk_id": {"S": f"{chzzk_id}"},
    }
    if counts_as_failure and fail_count >= MAX_NOTI_FAIL_COUNT:
        attrs["disable_notification"] = {"BOOL": True}
    return attrs
