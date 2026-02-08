import json
import logging
from typing import TypedDict

import requests
from user_agent import generate_user_agent

__all__ = ["ChzzkChannel", "ChzzkLive", "get_chzzk", "Following"]


class ChzzkChannel(TypedDict):
    channelId: str
    channelName: str
    channelImageUrl: str | None
    verifiedMark: bool


class ChzzkLive(TypedDict):
    liveId: int
    liveTitle: str
    status: str
    liveImageUrl: str
    defaultThumbnailImageUrl: str | None
    concurrentUserCount: int
    accumulateCount: int
    chatDonationRankingExposure: bool | None
    openDate: str
    closeDate: str
    adult: bool | None
    chatChannelId: str | None
    categoryType: str
    liveCategory: str
    liveCategoryValue: str
    chatActive: bool
    chatAvailableGroup: str
    paidPromotion: bool
    chatAvailableCondition: str
    minFollowerMinute: int
    livePlaybackJson: str
    channel: ChzzkChannel
    livePollingStatusJson: str
    userAdultStatus: str | None

    def __str__(self) -> str:
        return f"ChzzkLive(liveId={self.liveId}, liveTitle={self.liveTitle}, status={self.status})"

    def __repr__(self) -> str:
        return self.__str__()


class Streamer(TypedDict):
    openLive: bool


class Following(TypedDict):
    channel: ChzzkChannel
    liveInfo: ChzzkLive
    streamer: Streamer


def get_chzzk(
    channel_id: str, logger: logging.Logger | None = None, retry: int = 2
) -> ChzzkLive | None:
    """채널 ID를 통해 치지직 채널 정보를 가져옵니다.
    만약 채널이 존재하지 않는다면 None을 반환합니다.
    """
    # 정규화되지 않은 채널 ID
    if "/" in channel_id:
        if logger:
            logger.error(
                json.dumps(
                    {"type": "INVALID_CHZZK_CHANNEL_ID", "channel_id": channel_id}
                )
            )
        return None

    # retry
    for retry in range(1, retry + 1):
        try:
            res = requests.get(
                f"https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail",
                headers={
                    "User-Agent": generate_user_agent(os="win", device_type="desktop"),
                },
                timeout=1,
            )
            break
        except requests.exceptions.Timeout as e:
            if logger:
                logger.error(
                    json.dumps(
                        {
                            "type": "CHZZK_REQUEST_TIMEOUT",
                            "channel_id": channel_id,
                            "exception": str(e),
                            "retry": retry,
                        }
                    )
                )
        except Exception as e:
            if logger:
                logger.error(
                    json.dumps(
                        {
                            "type": "CHZZK_REQUEST_ERROR",
                            "channel_id": channel_id,
                            "exception": str(e),
                            "retry": retry,
                        }
                    )
                )
            continue
    else:
        # Break 없이 끝났을 때 -> retry 모두 실패
        if logger:
            logger.error(
                json.dumps({"type": "CHZZK_REQUEST_FAILED", "channel_id": channel_id})
            )
        return None

    # 채널이 존재하지 않는 경우 or 알 수 없는 오류
    if res.status_code != 200:
        if logger:
            logger.error(
                json.dumps(
                    {
                        "type": "CHZZK_INVALID_RESPONSE",
                        "channel_id": channel_id,
                        "status_code": res.status_code,
                        "response": res.text,
                    }
                )
            )
        return None

    content = res.json()["content"]

    # 한번도 방송을 키지 않은 경우
    if content is None:
        return None

    return content
